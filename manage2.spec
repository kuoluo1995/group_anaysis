# -*- mode: python ; coding: utf-8 -*-

block_cipher = None


a = Analysis(['manage.py'],
             pathex=['D:\\Anaconda3\\envs\\web\\Lib\\site-packages', 'E:\\PythonProjects\\group_anaysis'],
             binaries=[],
             datas=[(r'E:\PythonProjects\group_anaysis\services\configs',r'services\configs'),
                    (r'E:\PythonProjects\group_anaysis\dataset',r'dataset'),
                    (r'E:\PythonProjects\group_anaysis\templates',r'templates')],
             hiddenimports=['channels','channels.apps'],
             hookspath=[],
             runtime_hooks=[],
             excludes=[],
             win_no_prefer_redirects=False,
             win_private_assemblies=False,
             cipher=block_cipher,
             noarchive=False)
pyz = PYZ(a.pure, a.zipped_data,
             cipher=block_cipher)
exe = EXE(pyz,
          a.scripts,
          [],
          exclude_binaries=True,
          name='manage',
          debug=False,
          bootloader_ignore_signals=False,
          strip=False,
          upx=True,
          console=True )
coll = COLLECT(exe,
               a.binaries,
               a.zipfiles,
               a.datas,
               strip=False,
               upx=True,
               upx_exclude=[],
               name='manage')