from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from sqlalchemy.orm import joinedload
from app import db
from app.models.akademik import Santri, Pengajar, Kelas, MataPelajaran
from app.models.user import User
from app.forms.master import SantriForm, PengajarForm, KelasForm, MapelForm
from app.forms.auth import UserForm, UserEditForm
from app.decorators import admin_required

bp = Blueprint('master', __name__, url_prefix='/master')

# --- USER MANAGEMENT ---
@bp.route('/users')
@login_required
@admin_required
def user_list():
    users = User.query.all()
    return render_template('master/user_list.html', title='Manajemen User', users=users)

@bp.route('/users/add', methods=['GET', 'POST'])
@login_required
@admin_required
def user_add():
    form = UserForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            role=form.role.data
        )
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('User berhasil ditambahkan', 'success')
        return redirect(url_for('master.user_list'))
    return render_template('master/user_form.html', title='Tambah User', form=form)

@bp.route('/users/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def user_edit(id):
    user = User.query.get_or_404(id)
    form = UserEditForm(obj=user)
    
    if form.validate_on_submit():
        user.username = form.username.data
        user.role = form.role.data
        if form.password.data:
            user.set_password(form.password.data)
        db.session.commit()
        flash('User berhasil diperbarui', 'success')
        return redirect(url_for('master.user_list'))
        
    return render_template('master/user_form.html', title='Edit User', form=form)

@bp.route('/users/delete/<int:id>', methods=['POST'])
@login_required
@admin_required
def user_delete(id):
    if id == current_user.id:
        flash('Tidak dapat menghapus akun sendiri', 'danger')
        return redirect(url_for('master.user_list'))
        
    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash('User berhasil dihapus', 'success')
    return redirect(url_for('master.user_list'))

@bp.route('/santri')
@login_required
@admin_required
def santri_list():
    santris = Santri.query.options(joinedload(Santri.kelas)).all()
    return render_template('master/santri_list.html', title='Data Santri', santris=santris)

@bp.route('/kelas')
@login_required
@admin_required
def kelas_list():
    kelas_list = Kelas.query.options(joinedload(Kelas.wali_kelas)).all()
    return render_template('master/kelas_list.html', title='Data Kelas', kelas_list=kelas_list)
