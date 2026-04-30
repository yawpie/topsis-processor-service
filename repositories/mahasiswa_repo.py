from models.mahasiswa import Mahasiswa

def bulk_insert_mahasiswa(db, data_list):
    objects = [Mahasiswa(**data) for data in data_list]
    db.bulk_save_objects(objects)
    db.commit()