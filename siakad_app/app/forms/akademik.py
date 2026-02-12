from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, FloatField, DateField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length

class NilaiForm(FlaskForm):
    santri_id = SelectField('Santri', coerce=int, validators=[DataRequired()])
    mapel_id = SelectField('Mata Pelajaran', coerce=int, validators=[DataRequired()])
    semester = SelectField('Semester', choices=[
        ('Ganjil 2024/2025', 'Ganjil 2024/2025'),
        ('Genap 2024/2025', 'Genap 2024/2025'),
        ('Ganjil 2025/2026', 'Ganjil 2025/2026')
    ], validators=[DataRequired()])
    
    nilai_harian = FloatField('Nilai Harian', validators=[NumberRange(min=0, max=100)], default=0)
    nilai_uts = FloatField('Nilai UTS', validators=[NumberRange(min=0, max=100)], default=0)
    nilai_uas = FloatField('Nilai UAS', validators=[NumberRange(min=0, max=100)], default=0)
    nilai_praktik = FloatField('Nilai Praktik', validators=[NumberRange(min=0, max=100)], default=0)
    
    submit = SubmitField('Simpan Nilai')

class AbsensiForm(FlaskForm):
    santri_id = SelectField('Santri', coerce=int, validators=[DataRequired()])
    tanggal = DateField('Tanggal', validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('Hadir', 'Hadir'),
        ('Sakit', 'Sakit'),
        ('Izin', 'Izin'),
        ('Alpha', 'Alpha')
    ], validators=[DataRequired()])
    submit = SubmitField('Simpan Absensi')

class TahfidzForm(FlaskForm):
    santri_id = SelectField('Santri', coerce=int, validators=[DataRequired()])
    nama_surat = StringField('Nama Surat', validators=[DataRequired(), Length(max=50)])
    ayat = StringField('Ayat', validators=[DataRequired(), Length(max=50)])
    kelancaran = SelectField('Kelancaran', choices=[
        ('Lancar', 'Lancar'),
        ('Kurang Lancar', 'Kurang Lancar'),
        ('Ulang', 'Ulang')
    ], validators=[DataRequired()])
    tajwid = SelectField('Tajwid', choices=[
        ('Bagus', 'Bagus'),
        ('Cukup', 'Cukup'),
        ('Kurang', 'Kurang')
    ], validators=[DataRequired()])
    tanggal_setor = DateField('Tanggal Setor', validators=[DataRequired()])
    submit = SubmitField('Simpan Hafalan')

class RaportForm(FlaskForm):
    santri_id = SelectField('Santri', coerce=int, validators=[DataRequired()])
    semester = SelectField('Semester', choices=[
        ('Ganjil 2024/2025', 'Ganjil 2024/2025'),
        ('Genap 2024/2025', 'Genap 2024/2025'),
        ('Ganjil 2025/2026', 'Ganjil 2025/2026')
    ], validators=[DataRequired()])
    catatan_wali_kelas = TextAreaField('Catatan Wali Kelas', validators=[DataRequired()])
    status_kenaikan = SelectField('Status Kenaikan', choices=[
        ('Naik Kelas', 'Naik Kelas'),
        ('Tinggal Kelas', 'Tinggal Kelas'),
        ('Lulus', 'Lulus')
    ], validators=[DataRequired()])
    tanggal_bagi = DateField('Tanggal Bagi Raport', validators=[DataRequired()])
    submit = SubmitField('Simpan Raport')
