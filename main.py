#!/usr/bin/env python3
"""
GNOME Extensions Backup Tool
Ferramenta para fazer backup e restaurar extensões do GNOME Shell
"""

import gi
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')
from gi.repository import Gtk, Adw, GLib, Gio
import os
import subprocess
import shutil
import tarfile
from pathlib import Path
from datetime import datetime

class BackupApp(Adw.Application):
    def __init__(self):
        super().__init__(application_id='com.example.gnome-backup',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)
        self.extensions_path = Path.home() / '.local/share/gnome-shell/extensions'
        
    def do_activate(self):
        win = BackupWindow(application=self)
        win.present()

class ExtensionRow(Adw.ActionRow):
    def __init__(self, extension_name):
        super().__init__()
        self.extension_name = extension_name
        self.set_title(extension_name)
        
        # Ícone
        icon = Gtk.Image.new_from_icon_name("application-x-addon-symbolic")
        self.add_prefix(icon)
        
        # Checkbox
        self.checkbox = Gtk.CheckButton()
        self.checkbox.set_active(True)  # Todas marcadas por padrão
        self.add_suffix(self.checkbox)
        
    def is_selected(self):
        return self.checkbox.get_active()
    
    def set_selected(self, selected):
        self.checkbox.set_active(selected)

class BackupWindow(Adw.ApplicationWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.set_title("Backup de Extensões GNOME 1.0")
        self.set_default_size(600, 550)
        
        self.extension_rows = []
        
        # Header bar
        header = Adw.HeaderBar()
        
        # Main box
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        
        # Toolbar view
        toolbar_view = Adw.ToolbarView()
        toolbar_view.add_top_bar(header)
        
        # Content box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=20)
        content_box.set_margin_top(20)
        content_box.set_margin_bottom(20)
        content_box.set_margin_start(20)
        content_box.set_margin_end(20)
        
        # Title
        title = Gtk.Label(label="Gerenciador de Backup 1.0")
        title.add_css_class('title-1')
        content_box.append(title)
        
        # Description
        description = Gtk.Label(
            label="Faça backup ou restaure suas extensões e configurações do GNOME"
        )
        description.add_css_class('dim-label')
        description.set_wrap(True)
        content_box.append(description)
        
        # Selection controls box
        selection_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        selection_box.set_halign(Gtk.Align.START)
        
        # Select all button
        select_all_btn = Gtk.Button(label="Selecionar Todas")
        select_all_btn.connect('clicked', self.on_select_all_clicked)
        selection_box.append(select_all_btn)
        
        # Deselect all button
        deselect_all_btn = Gtk.Button(label="Desmarcar Todas")
        deselect_all_btn.connect('clicked', self.on_deselect_all_clicked)
        selection_box.append(deselect_all_btn)
        
        # Counter label
        self.counter_label = Gtk.Label(label="")
        self.counter_label.add_css_class('dim-label')
        self.counter_label.set_margin_start(10)
        selection_box.append(self.counter_label)
        
        content_box.append(selection_box)
        
        # Extensions list
        list_frame = Gtk.Frame()
        list_frame.set_margin_top(10)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_min_content_height(200)
        scrolled.set_vexpand(True)
        
        self.extensions_list = Gtk.ListBox()
        self.extensions_list.add_css_class('boxed-list')
        scrolled.set_child(self.extensions_list)
        
        list_frame.set_child(scrolled)
        content_box.append(list_frame)
        
        # Load extensions
        self.load_extensions()
        
        # Status label
        self.status_label = Gtk.Label(label="")
        self.status_label.add_css_class('dim-label')
        content_box.append(self.status_label)
        
        # Progress bar
        self.progress_bar = Gtk.ProgressBar()
        self.progress_bar.set_visible(False)
        content_box.append(self.progress_bar)
        
        # Buttons box
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        buttons_box.set_halign(Gtk.Align.CENTER)
        buttons_box.set_margin_top(10)
        
        # Backup button
        backup_btn = Gtk.Button(label="Fazer Backup")
        backup_btn.add_css_class('suggested-action')
        backup_btn.add_css_class('pill')
        backup_btn.set_size_request(150, -1)
        backup_btn.connect('clicked', self.on_backup_clicked)
        buttons_box.append(backup_btn)
        
        # Restore button
        restore_btn = Gtk.Button(label="Restaurar Backup")
        restore_btn.add_css_class('pill')
        restore_btn.set_size_request(150, -1)
        restore_btn.connect('clicked', self.on_restore_clicked)
        buttons_box.append(restore_btn)
        
        content_box.append(buttons_box)
        
        toolbar_view.set_content(content_box)
        self.set_content(toolbar_view)
        
    def load_extensions(self):
        """Carrega a lista de extensões instaladas"""
        extensions_path = Path.home() / '.local/share/gnome-shell/extensions'
        
        # Limpa a lista atual
        self.extension_rows = []
        while True:
            row = self.extensions_list.get_row_at_index(0)
            if row is None:
                break
            self.extensions_list.remove(row)
        
        if not extensions_path.exists():
            row = Adw.ActionRow(title="Nenhuma extensão encontrada")
            self.extensions_list.append(row)
            return
            
        extensions = sorted([d for d in extensions_path.iterdir() if d.is_dir()])
        
        if not extensions:
            row = Adw.ActionRow(title="Nenhuma extensão encontrada")
            self.extensions_list.append(row)
            return
        
        for ext in extensions:
            row = ExtensionRow(ext.name)
            self.extension_rows.append(row)
            self.extensions_list.append(row)
        
        self.update_counter()
    
    def on_select_all_clicked(self, button):
        """Seleciona todas as extensões"""
        for row in self.extension_rows:
            row.set_selected(True)
        self.update_counter()
    
    def on_deselect_all_clicked(self, button):
        """Desmarca todas as extensões"""
        for row in self.extension_rows:
            row.set_selected(False)
        self.update_counter()
    
    def update_counter(self):
        """Atualiza o contador de extensões selecionadas"""
        selected_count = sum(1 for row in self.extension_rows if row.is_selected())
        total_count = len(self.extension_rows)
        self.counter_label.set_text(f"📦 {selected_count} de {total_count} selecionadas")
    
    def get_selected_extensions(self):
        """Retorna lista de extensões selecionadas"""
        return [row.extension_name for row in self.extension_rows if row.is_selected()]
    
    def on_backup_clicked(self, button):
        """Callback para o botão de backup"""
        selected = self.get_selected_extensions()
        if not selected:
            self.show_error_dialog("Selecione pelo menos uma extensão para fazer backup!")
            return
        
        dialog = Gtk.FileDialog()
        dialog.set_title("Salvar Backup")
        dialog.set_initial_name(f"gnome-extensions-backup-{datetime.now().strftime('%Y%m%d-%H%M%S')}.tar.gz")
        
        dialog.save(self, None, self.on_backup_location_selected)
    
    def on_backup_location_selected(self, dialog, result):
        """Callback quando o local de backup é selecionado"""
        try:
            file = dialog.save_finish(result)
            if file:
                backup_path = file.get_path()
                self.perform_backup(backup_path)
        except Exception as e:
            print(f"Erro ao selecionar local: {e}")
    
    def perform_backup(self, backup_path):
        """Realiza o backup das extensões selecionadas"""
        selected = self.get_selected_extensions()
        self.status_label.set_text(f"Fazendo backup de {len(selected)} extensões...")
        self.progress_bar.set_visible(True)
        self.progress_bar.pulse()
        
        try:
            extensions_path = Path.home() / '.local/share/gnome-shell/extensions'
            settings_file = Path('/tmp/gnome-extensions-settings.dconf')
            
            # Exportar configurações do dconf
            with open(settings_file, 'w') as f:
                subprocess.run(['dconf', 'dump', '/org/gnome/shell/extensions/'],
                             stdout=f, check=True)
            
            # Criar arquivo tar.gz
            with tarfile.open(backup_path, 'w:gz') as tar:
                # Adicionar apenas extensões selecionadas
                for ext_name in selected:
                    ext_path = extensions_path / ext_name
                    if ext_path.exists():
                        tar.add(ext_path, arcname=f'extensions/{ext_name}')
                
                # Adicionar configurações
                tar.add(settings_file, arcname='settings.dconf')
            
            # Limpar arquivo temporário
            settings_file.unlink()
            
            self.status_label.set_text(f"✓ Backup de {len(selected)} extensões concluído!")
            self.progress_bar.set_visible(False)
            
            # Mostrar diálogo de sucesso
            self.show_success_dialog(f"Backup de {len(selected)} extensões realizado com sucesso!")
            
        except Exception as e:
            self.status_label.set_text(f"✗ Erro ao fazer backup: {str(e)}")
            self.progress_bar.set_visible(False)
            self.show_error_dialog(f"Erro ao fazer backup: {str(e)}")
    
    def on_restore_clicked(self, button):
        """Callback para o botão de restauração"""
        dialog = Gtk.FileDialog()
        dialog.set_title("Selecionar Backup")
        
        # Filtro para arquivos .tar.gz
        filter_tar = Gtk.FileFilter()
        filter_tar.set_name("Arquivos de Backup (*.tar.gz)")
        filter_tar.add_pattern("*.tar.gz")
        
        filters = Gio.ListStore.new(Gtk.FileFilter)
        filters.append(filter_tar)
        dialog.set_filters(filters)
        
        dialog.open(self, None, self.on_restore_location_selected)
    
    def on_restore_location_selected(self, dialog, result):
        """Callback quando o arquivo de backup é selecionado"""
        try:
            file = dialog.open_finish(result)
            if file:
                backup_path = file.get_path()
                self.perform_restore(backup_path)
        except Exception as e:
            print(f"Erro ao selecionar arquivo: {e}")
    
    def perform_restore(self, backup_path):
        """Restaura o backup das extensões"""
        self.status_label.set_text("Restaurando backup...")
        self.progress_bar.set_visible(True)
        self.progress_bar.pulse()
        
        try:
            temp_dir = Path('/tmp/gnome-backup-restore')
            extensions_path = Path.home() / '.local/share/gnome-shell/extensions'
            
            # Criar diretório temporário
            if temp_dir.exists():
                shutil.rmtree(temp_dir)
            temp_dir.mkdir()
            
            # Extrair backup
            with tarfile.open(backup_path, 'r:gz') as tar:
                tar.extractall(temp_dir)
            
            # Restaurar extensões
            restored_extensions = temp_dir / 'extensions'
            count = 0
            if restored_extensions.exists():
                # Criar pasta de extensões se não existir
                extensions_path.mkdir(parents=True, exist_ok=True)
                
                # Copiar extensões
                for ext in restored_extensions.iterdir():
                    dest = extensions_path / ext.name
                    if dest.exists():
                        shutil.rmtree(dest)
                    shutil.copytree(ext, dest)
                    count += 1
            
            # Restaurar configurações
            settings_file = temp_dir / 'settings.dconf'
            if settings_file.exists():
                with open(settings_file, 'r') as f:
                    subprocess.run(['dconf', 'load', '/org/gnome/shell/extensions/'],
                                 stdin=f, check=True)
            
            # Limpar diretório temporário
            shutil.rmtree(temp_dir)
            
            self.status_label.set_text(f"✓ {count} extensões restauradas! Reinicie o GNOME Shell (Alt+F2, digite 'r')")
            self.progress_bar.set_visible(False)
            
            # Recarregar lista de extensões
            self.load_extensions()
            
            # Mostrar diálogo de sucesso
            self.show_success_dialog(f"{count} extensões restauradas com sucesso!\n\nReinicie o GNOME Shell (Alt+F2, digite 'r') para aplicar as mudanças.")
            
        except Exception as e:
            self.status_label.set_text(f"✗ Erro ao restaurar: {str(e)}")
            self.progress_bar.set_visible(False)
            self.show_error_dialog(f"Erro ao restaurar backup: {str(e)}")
    
    def show_success_dialog(self, message):
        """Mostra diálogo de sucesso"""
        dialog = Adw.MessageDialog.new(self)
        dialog.set_heading("Sucesso")
        dialog.set_body(message)
        dialog.add_response("ok", "OK")
        dialog.set_default_response("ok")
        dialog.set_close_response("ok")
        dialog.present()
    
    def show_error_dialog(self, message):
        """Mostra diálogo de erro"""
        dialog = Adw.MessageDialog.new(self)
        dialog.set_heading("Erro")
        dialog.set_body(message)
        dialog.add_response("ok", "OK")
        dialog.set_default_response("ok")
        dialog.set_close_response("ok")
        dialog.present()

def main():
    app = BackupApp()
    return app.run(None)

if __name__ == '__main__':
    main()
