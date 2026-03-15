# launcher.spec — bundles EVERYTHING into one exe
block_cipher = None

a = Analysis(
    ['launcher.py'],
    pathex=['.'],
    binaries=[],
    datas=[
        ('static', 'static'),
        ('server.py', '.'),
    ],
    hiddenimports=[
        'uvicorn',
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'fastapi',
        'starlette',
        'starlette.staticfiles',
        'starlette.responses',
        'starlette.routing',
        'pydantic',
        'pydantic.deprecated',
        'pydantic.deprecated.class_validators',
        'anyio',
        'anyio._backends._asyncio',
        'win32file',
        'win32pipe',
        'tkinter',
        'tkinter.messagebox',
        'email.mime.multipart',
        'multipart',
        'python_multipart',
    ],
    hookspath=[],
    runtime_hooks=[],
    excludes=['matplotlib', 'numpy', 'pandas', 'scipy', 'PyQt5', 'wx'],
    cipher=block_cipher,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='SoundLaunch',
    debug=False,
    strip=False,
    upx=True,
    console=False,
    icon='static/icon.png',
)
