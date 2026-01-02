from auth.routes import auth_bp

print('Import OK')
print(f'Blueprint name: {auth_bp.name}')
print(f'URL prefix: {auth_bp.url_prefix}')
