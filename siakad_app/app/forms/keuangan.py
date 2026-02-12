from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DecimalField, DateField, SubmitField
from wtforms.validators import DataRequired, NumberRange

class PembayaranForm(FlaskForm):
    santri_id = SelectField('Santri', coerce=int, validators=[DataRequired()])
    bulan = SelectField('Bulan', choices=[
        ('Januari', 'Januari'), ('Februari', 'Februari'), ('Maret', 'Maret'),
        ('April', 'April'), ('Mei', 'Mei'), ('Juni', 'Juni'),
        ('Juli', 'Juli'), ('Agustus', 'Agustus'), ('September', 'September'),
        ('Oktober', 'Oktober'), ('November', 'November'), ('Desember', 'Desember')
    ], validators=[DataRequired()])
    tahun = SelectField('Tahun', coerce=int, validators=[DataRequired()])
    jumlah = DecimalField('Jumlah (Rp)', validators=[DataRequired(), NumberRange(min=0)])
    status = SelectField('Status', choices=[('Lunas', 'Lunas'), ('Belum Lunas', 'Belum Lunas')], validators=[DataRequired()])
    tanggal_bayar = DateField('Tanggal Bayar', validators=[DataRequired()])
    submit = SubmitField('Simpan')
