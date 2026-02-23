from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import SelectField, IntegerField, FloatField, DateField, SubmitField, StringField, TextAreaField
from wtforms.validators import DataRequired, NumberRange, Length, Optional

class NilaiForm(FlaskForm):
    santri_id = SelectField('Santri', coerce=int, validators=[DataRequired()])
    mapel_id = SelectField('Mata Pelajaran', coerce=int, validators=[DataRequired()])
    semester = SelectField('Semester', validators=[DataRequired()])
    
    nilai_harian = FloatField('Nilai Harian (30%)', validators=[NumberRange(min=0, max=100)], default=0)
    nilai_kehadiran = FloatField('Nilai Kehadiran (30%)', validators=[NumberRange(min=0, max=100)], default=0)
    nilai_uas = FloatField('Nilai Ulangan/UAS (40%)', validators=[NumberRange(min=0, max=100)], default=0)
    
    # Legacy / Optional
    nilai_uts = FloatField('Nilai UTS (Opsional)', validators=[NumberRange(min=0, max=100)], default=0)
    nilai_praktik = FloatField('Nilai Praktik (Opsional)', validators=[NumberRange(min=0, max=100)], default=0)
    
    deskripsi = TextAreaField('Deskripsi / Catatan (Opsional)')
    
    submit = SubmitField('Simpan Nilai')

    def __init__(self, *args, **kwargs):
        super(NilaiForm, self).__init__(*args, **kwargs)
        # Generate dynamic semester choices
        current_year = datetime.now().year
        choices = []
        # Last 2 years and Next 1 year
        for year in range(current_year - 2, current_year + 2):
            next_year = year + 1
            choices.append((f'Ganjil {year}/{next_year}', f'Ganjil {year}/{next_year}'))
            choices.append((f'Genap {year}/{next_year}', f'Genap {year}/{next_year}'))
        # Sort descending (newest first)
        choices.sort(key=lambda x: x[0], reverse=True)
        self.semester.choices = choices

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

class AbsensiMassalForm(FlaskForm):
    kelas_id = SelectField('Kelas', coerce=int, validators=[DataRequired()])
    tanggal = DateField('Tanggal', validators=[DataRequired()], default=datetime.utcnow)
    submit = SubmitField('Tampilkan Siswa')

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
    semester = SelectField('Semester', validators=[DataRequired()])
    catatan_wali_kelas = TextAreaField('Catatan Wali Kelas', validators=[DataRequired()])
    status_kenaikan = SelectField('Status Kenaikan', choices=[
        ('Naik Kelas', 'Naik Kelas'),
        ('Tinggal Kelas', 'Tinggal Kelas'),
        ('Lulus', 'Lulus')
    ], validators=[DataRequired()])
    tanggal_bagi = DateField('Tanggal Bagi Raport', validators=[DataRequired()])
    
    # Nilai Sikap / Kepribadian
    sikap_akhlak = SelectField('Akhlak', choices=[('Sangat Baik', 'Sangat Baik'), ('Baik', 'Baik'), ('Cukup', 'Cukup'), ('Kurang', 'Kurang')], default='Baik')
    sikap_kerajinan = SelectField('Kerajinan', choices=[('Sangat Baik', 'Sangat Baik'), ('Baik', 'Baik'), ('Cukup', 'Cukup'), ('Kurang', 'Kurang')], default='Baik')
    sikap_kedisiplinan = SelectField('Kedisiplinan', choices=[('Sangat Baik', 'Sangat Baik'), ('Baik', 'Baik'), ('Cukup', 'Cukup'), ('Kurang', 'Kurang')], default='Baik')
    sikap_kebersihan = SelectField('Kebersihan', choices=[('Sangat Baik', 'Sangat Baik'), ('Baik', 'Baik'), ('Cukup', 'Cukup'), ('Kurang', 'Kurang')], default='Baik')
    
    # Laporan Perkembangan (Khusus LPQ)
    deskripsi_moral = TextAreaField('Perkembangan Nilai Moral dan Agama')
    deskripsi_kognitif = TextAreaField('Perkembangan Kognitif')
    deskripsi_sosial = TextAreaField('Perkembangan Sosial Emosional')
    deskripsi_bahasa = TextAreaField('Perkembangan Bahasa / Bicara')
    deskripsi_seni = TextAreaField('Perkembangan Seni dan Keterampilan')
    deskripsi_diri = TextAreaField('Pengembangan Diri')
    
    # Statistik Absensi (Snapshot)
    sakit = IntegerField('Sakit', validators=[NumberRange(min=0)], default=0)
    izin = IntegerField('Izin', validators=[NumberRange(min=0)], default=0)
    alpha = IntegerField('Alpha', validators=[NumberRange(min=0)], default=0)
    
    # Ranking (Manual Override)
    rank = IntegerField('Peringkat Kelas (Manual)', validators=[Optional(), NumberRange(min=1)])
    total_students = IntegerField('Total Santri', validators=[Optional(), NumberRange(min=1)])
    
    submit = SubmitField('Simpan Raport')

    def __init__(self, *args, **kwargs):
        super(RaportForm, self).__init__(*args, **kwargs)
        # Generate dynamic semester choices
        current_year = datetime.now().year
        choices = []
        # Last 2 years and Next 1 year
        for year in range(current_year - 2, current_year + 2):
            next_year = year + 1
            choices.append((f'Ganjil {year}/{next_year}', f'Ganjil {year}/{next_year}'))
            choices.append((f'Genap {year}/{next_year}', f'Genap {year}/{next_year}'))
        # Sort descending
        choices.sort(key=lambda x: x[0], reverse=True)
        self.semester.choices = choices
