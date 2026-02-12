from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length, ValidationError
from app.models.akademik import Santri

class SantriForm(FlaskForm):
    nis = StringField('NIS', validators=[DataRequired(), Length(max=20)])
    nama = StringField('Nama Lengkap', validators=[DataRequired(), Length(max=100)])
    jenis_kelamin = SelectField('Jenis Kelamin', choices=[('L', 'Laki-laki'), ('P', 'Perempuan')], validators=[DataRequired()])
    tanggal_lahir = DateField('Tanggal Lahir', validators=[DataRequired()])
    alamat = TextAreaField('Alamat')
    jenjang = SelectField('Jenjang', choices=[('SD', 'SD'), ('SMP', 'SMP'), ('SMA', 'SMA')], validators=[DataRequired()])
    status = SelectField('Status', choices=[('aktif', 'Aktif'), ('lulus', 'Lulus'), ('keluar', 'Keluar')], default='aktif')
    kelas_id = SelectField('Kelas', coerce=int)
    submit = SubmitField('Simpan')

    def __init__(self, original_nis=None, *args, **kwargs):
        super(SantriForm, self).__init__(*args, **kwargs)
        self.original_nis = original_nis

    def validate_nis(self, nis):
        if self.original_nis and nis.data == self.original_nis:
            return
        user = Santri.query.filter_by(nis=nis.data).first()
        if user:
            raise ValidationError('NIS sudah terdaftar.')

class PengajarForm(FlaskForm):
    nama = StringField('Nama Lengkap', validators=[DataRequired(), Length(max=100)])
    no_hp = StringField('No. HP', validators=[Length(max=20)])
    alamat = TextAreaField('Alamat')
    submit = SubmitField('Simpan')

class KelasForm(FlaskForm):
    nama_kelas = StringField('Nama Kelas', validators=[DataRequired(), Length(max=50)])
    jenjang = SelectField('Jenjang', choices=[('SD', 'SD'), ('SMP', 'SMP'), ('SMA', 'SMA')], validators=[DataRequired()])
    wali_kelas_id = SelectField('Wali Kelas', coerce=int)
    submit = SubmitField('Simpan')

class MapelForm(FlaskForm):
    nama_mapel = StringField('Nama Mata Pelajaran', validators=[DataRequired(), Length(max=100)])
    jenjang = SelectField('Jenjang', choices=[('SD', 'SD'), ('SMP', 'SMP'), ('SMA', 'SMA')], validators=[DataRequired()])
    submit = SubmitField('Simpan')
