from enum import Enum as PyEnum
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, JSON, Enum
from sqlalchemy.types import Numeric
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, validates
from datetime import datetime
from config import settings

Base = declarative_base()
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True, echo=False)
SessionLocal = sessionmaker(bind=engine)

class PreservationType(PyEnum):
    # 保全类型
    PROPERTY = "财产保全"
    BEHAVIOR = "行为保全"
    EVIDENCE = "证据保全"

class PreservationCategory(PyEnum):
    # 保全类别
    BEFORE_LAWSUIT = "诉前保全"
    DURING_LAWSUIT = "诉中保全"
    BEFORE_EXECUTION = "执行前保全"

class GuaranteeStatus(PyEnum):
    # 担保情况
    PROVIDED = "已提供"
    NOT_PROVIDED = "未提供"
    WAIVED = "免除"

class SubmitterType(PyEnum):
    # 提交身份人
    PARTY = "当事人"
    AGENT = "代理人"
    LAWYER = "律师"

class CaseStatus(PyEnum):
    # 案件状态
    PENDING = "待立案"
    FILLING = "填写中"
    UPLOADING = "上传中"
    SUBMITTING = "提交中"
    SUBMITTED = "已提交"
    FAILED = "失败"
    REJECTED = "已驳回"

class Court(Base):
    __tablename__ = "courts"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, comment="法院名称")
    province = Column(String(50), comment="省份")
    city = Column(String(50), comment="城市")
    is_active = Column(Integer, default=1, comment="是否启用")
    created_at = Column(DateTime, default=datetime.now)
    
    def __repr__(self):
        return f"<Court(id={self.id}, name={self.name})>"

class Party(Base):
    __tablename__ = "parties"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, comment="姓名")
    id_card = Column(String(18), comment="身份证号")
    phone = Column(String(20), comment="电话")
    address = Column(String(200), comment="地址")
    party_type = Column(String(10), comment="类型: 原告/被告/第三人")
    created_at = Column(DateTime, default=datetime.now)
    
    @validates('id_card')
    def validate_id_card(self, key, value):
        if value and len(value) not in [15, 18]:
            raise ValueError(f"身份证号长度错误: {len(value)}")
        return value
    
    def __repr__(self):
        return f"<Party(id={self.id}, name={self.name})>"

class Case(Base):
    __tablename__ = "cases"
    
    id = Column(Integer, primary_key=True)
    case_no = Column(String(50), unique=True, comment="案件编号")
    
    # 保全基本信息
    court_id = Column(Integer, comment="法院ID")
    preservation_type = Column(String(20), comment="保全类型")
    preservation_category = Column(String(20), comment="保全类别")
    apply_amount = Column(Numeric(15, 2), comment="申请保全金额")
    guarantee_status = Column(String(10), comment="担保情况")
    submitter_type = Column(String(20), comment="提交身份人")
    
    # 申请人（法人）
    applicant_name = Column(String(100), comment="单位名称")
    applicant_cert_type = Column(String(50), comment="证照类型")
    applicant_cert_no = Column(String(50), comment="证照号码")
    applicant_legal_person = Column(String(50), comment="法定代表人")
    applicant_phone = Column(String(20), comment="联系电话")
    applicant_address = Column(String(200), comment="单位地址")
    
    # 被申请人（自然人）
    respondent_name = Column(String(50), comment="姓名")
    respondent_id_card = Column(String(18), comment="身份证号")
    respondent_gender = Column(String(10), comment="性别")
    respondent_address = Column(String(200), comment="住址")
    
    # 代理人
    agent_name = Column(String(50), comment="姓名")
    agent_id_card = Column(String(18), comment="身份证号")
    agent_phone = Column(String(20), comment="电话")
    agent_cert_no = Column(String(50), comment="执业证号")
    agent_law_firm = Column(String(100), comment="律所")
    
    # 财产线索
    property_clues = Column(JSON, comment="财产线索列表")
    
    # 担保信息
    guarantor = Column(String(100), comment="担保人")
    guarantee_value = Column(Numeric(15, 2), comment="担保价值")
    
    # 材料路径
    materials_dir = Column(String(500), comment="材料目录")
    preservation_application = Column(String(200), comment="保全申请书")
    indictment = Column(String(200), comment="起诉状")
    id_card_files = Column(JSON, comment="身份证明文件列表")
    guarantee_files = Column(JSON, comment="担保材料列表")
    evidence_files = Column(JSON, comment="证据材料列表")
    other_files = Column(JSON, comment="其他材料列表")
    
    # 状态
    status = Column(String(20), default=CaseStatus.PENDING.value, comment="状态")
    court_case_no = Column(String(50), comment="法院案号")
    submit_time = Column(DateTime, comment="提交时间")
    fail_reason = Column(Text, comment="失败原因")
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    
    @validates('apply_amount', 'guarantee_value')
    def validate_amount(self, key, value):
        if value is not None and value < 0:
            raise ValueError(f"{key} 不能为负数")
        return value
    
    @validates('respondent_id_card', 'agent_id_card')
    def validate_id_card(self, key, value):
        if value and len(value) not in [15, 18]:
            raise ValueError(f"身份证号长度错误: {len(value)}")
        return value
    
    def __repr__(self):
        return f"<Case(id={self.id}, case_no={self.case_no}, status={self.status})>"
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "case_no": self.case_no,
            "status": self.status,
            "court_case_no": self.court_case_no,
            "applicant_name": self.applicant_name,
            "respondent_name": self.respondent_name,
            "apply_amount": float(self.apply_amount) if self.apply_amount else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "submit_time": self.submit_time.isoformat() if self.submit_time else None,
        }

def init_db():
    Base.metadata.create_all(engine)
    print("数据库表创建完成")
    
    # 创建默认法院数据
    db = SessionLocal()
    try:
        if not db.query(Court).first():
            default_courts = [
                Court(name="北京市第一中级人民法院", province="北京市", city="北京市"),
                Court(name="北京市第二中级人民法院", province="北京市", city="北京市"),
                Court(name="北京市海淀区人民法院", province="北京市", city="北京市"),
                Court(name="北京市朝阳区人民法院", province="北京市", city="北京市"),
            ]
            db.add_all(default_courts)
            db.commit()
            print("默认法院数据已创建")
    finally:
        db.close()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
