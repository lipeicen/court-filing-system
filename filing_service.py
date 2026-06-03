import asyncio
import logging
from pathlib import Path
from datetime import datetime
from functools import wraps

from core.browser_controller import CourtBrowser
from models import SessionLocal, Case, Court, CaseStatus
from config import settings

logger = logging.getLogger(__name__)

def retry(max_attempts: int = 3, delay: float = 2.0):
    # 重试装饰器
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    logger.warning(f"{func.__name__} 第 {attempt}/{max_attempts} 次尝试失败: {e}")
                    if attempt < max_attempts:
                        await asyncio.sleep(delay * attempt)
            raise last_exception
        return wrapper
    return decorator

class FilingService:
    # 立案服务
    
    def __init__(self):
        self.browser = CourtBrowser()
        self.db = SessionLocal()
    
    async def initialize(self):
        # 初始化
        await self.browser.launch()
        login_success = await self.browser.login()
        if not login_success:
            raise Exception("登录失败")
    
    @retry(max_attempts=2, delay=3.0)
    async def process_case(self, case_id: int) -> dict:
        # 处理单个案件
        case = self.db.query(Case).filter(Case.id == case_id).first()
        if not case:
            return {"error": "案件不存在"}
        
        # 更新状态为填写中
        self._update_status(case, CaseStatus.FILLING)
        
        try:
            court = self.db.query(Court).filter(Court.id == case.court_id).first()
            materials_dir = Path(case.materials_dir) if case.materials_dir else settings.MATERIALS_BASE_PATH / case.case_no
            
            # 1. 开始保全
            logger.info(f"案件 {case.case_no}: 开始保全流程")
            await self.browser.start_preservation()
            
            # 2. 填写基本信息
            logger.info(f"案件 {case.case_no}: 填写基本信息")
            await self.browser.fill_basic_info({
                "court_name": court.name if court else "",
                "preservation_type": case.preservation_type or "财产保全",
                "preservation_category": case.preservation_category or "诉中保全",
                "apply_amount": float(case.apply_amount) if case.apply_amount else 0,
                "guarantee_status": case.guarantee_status or "已提供",
                "submitter_type": case.submitter_type or "代理人"
            })
            
            # 3. 填写申请人
            if case.applicant_name:
                logger.info(f"案件 {case.case_no}: 填写申请人")
                await self.browser.fill_applicant({
                    "name": case.applicant_name,
                    "cert_no": case.applicant_cert_no or "",
                    "legal_person": case.applicant_legal_person or "",
                    "phone": case.applicant_phone or "",
                    "address": case.applicant_address or ""
                })
            
            # 4. 填写被申请人
            if case.respondent_name:
                logger.info(f"案件 {case.case_no}: 填写被申请人")
                await self.browser.fill_respondent({
                    "name": case.respondent_name,
                    "id_card": case.respondent_id_card or "",
                    "gender": case.respondent_gender or "男",
                    "address": case.respondent_address or ""
                })
            
            # 5. 填写代理人
            if case.agent_name:
                logger.info(f"案件 {case.case_no}: 填写代理人")
                await self.browser.fill_agent({
                    "name": case.agent_name,
                    "id_card": case.agent_id_card or "",
                    "phone": case.agent_phone or "",
                    "cert_no": case.agent_cert_no or "",
                    "law_firm": case.agent_law_firm or ""
                })
            
            # 6. 填写财产线索
            if case.property_clues:
                logger.info(f"案件 {case.case_no}: 填写财产线索")
                await self.browser.fill_property_clues(case.property_clues)
            
            # 7. 填写担保信息
            if case.guarantee_value:
                logger.info(f"案件 {case.case_no}: 填写担保信息")
                await self.browser.fill_guarantee({
                    "guarantor": case.guarantor or "",
                    "value": float(case.guarantee_value),
                    "description": ""
                })
            
            # 8. 上传材料
            self._update_status(case, CaseStatus.UPLOADING)
            await self._upload_materials(case, materials_dir)
            
            # 9. 提交
            self._update_status(case, CaseStatus.SUBMITTING)
            logger.info(f"案件 {case.case_no}: 提交申请")
            result = await self.browser.preview_and_submit()
            
            # 更新结果
            if result["success"]:
                self._update_status(case, CaseStatus.SUBMITTED, {
                    "court_case_no": result.get("court_case_no"),
                    "submit_time": datetime.now()
                })
                logger.info(f"案件 {case.case_no}: 提交成功，法院案号: {result.get('court_case_no')}")
            else:
                self._update_status(case, CaseStatus.FAILED, {
                    "fail_reason": result.get("message")
                })
                logger.error(f"案件 {case.case_no}: 提交失败 - {result.get('message')}")
            
            return result
            
        except Exception as e:
            logger.error(f"案件 {case_id} 处理失败: {e}")
            self._update_status(case, CaseStatus.FAILED, {"fail_reason": str(e)})
            return {"error": str(e)}
    
    async def _upload_materials(self, case: Case, materials_dir: Path):
        # 上传材料
        logger.info(f"案件 {case.case_no}: 上传材料...")
        
        uploads = [
            (case.preservation_application, "保全申请书"),
            (case.indictment, "起诉状"),
        ]
        
        for file_name, category in uploads:
            if file_name:
                file_path = materials_dir / file_name
                await self.browser.upload_file(str(file_path), category)
        
        # 批量上传其他材料
        for file_list, category in [
            (case.id_card_files or [], "身份证明材料"),
            (case.guarantee_files or [], "担保材料"),
            (case.evidence_files or [], "证据材料"),
            (case.other_files or [], "其他材料"),
        ]:
            for file_name in file_list:
                file_path = materials_dir / file_name
                await self.browser.upload_file(str(file_path), category)
    
    def _update_status(self, case: Case, status: CaseStatus, extra: dict = None):
        # 更新案件状态
        case.status = status.value
        if extra:
            for key, value in extra.items():
                if hasattr(case, key):
                    setattr(case, key, value)
        self.db.commit()
        logger.info(f"案件 {case.case_no}: 状态更新为 {status.value}")
    
    async def run_batch(self, limit: int = 10, status_filter: str = "待立案"):
        # 批量处理
        cases = self.db.query(Case).filter(Case.status == status_filter).limit(limit).all()
        results = []
        
        logger.info(f"批量处理 {len(cases)} 个案件")
        
        for case in cases:
            logger.info(f"处理案件: {case.case_no}")
            try:
                result = await self.process_case(case.id)
                results.append({
                    "case_id": case.id,
                    "case_no": case.case_no,
                    "success": result.get("success", False),
                    "message": result.get("message", "") or result.get("error", "")
                })
            except Exception as e:
                logger.error(f"案件 {case.case_no} 异常: {e}")
                results.append({
                    "case_id": case.id,
                    "case_no": case.case_no,
                    "success": False,
                    "message": str(e)
                })
            
            await asyncio.sleep(5)  # 间隔5秒
        
        return results
    
    async def close(self):
        # 关闭服务
        await self.browser.close()
        self.db.close()
        logger.info("服务已关闭")
