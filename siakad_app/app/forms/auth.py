from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
from app.models.user import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Ingat Saya')
    submit = SubmitField('Masuk')

class UserForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Konfirmasi Password', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Role', choices=[
        ('admin', 'Admin'),
        ('ustadz', 'Ustadz'),
        ('wali_santri', 'Wali Santri'),
        ('santri', 'Santri')
    ], validators=[DataRequired()])
    submit = SubmitField('Simpan User')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username sudah digunakan. Silakan gunakan username lain.')

class UserEditForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    password = PasswordField('Password (Kosongkan jika tidak ingin mengubah)')
    role = SelectField('Role', choices=[
        ('admin', 'Admin'),
        ('ustadz', 'Ustadz'),
        ('wali_santri', 'Wali Santri'),
        ('santri', 'Santri')
    ], validators=[DataRequired()])
    submit = SubmitField('Simpan Perubahan')
