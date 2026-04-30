from sqlalchemy import Column, Integer, String, Float
from core.database import Base

class Mahasiswa(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True) 
    nama = Column(String) 
    ipk = Column(Float) # benefit
    semester = Column(Integer) # cost
    penghasilan_ortu = Column(Integer) # cost
    jumlah_tanggungan = Column(Integer) # benefit
    keaktifan_organisasi = Column(String) # benefit
    skor_prestasi = Column(Float) # benefit