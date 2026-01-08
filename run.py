#!/usr/bin/env python3
from powerdnsadmin import create_app

if __name__ == '__main__':
    app = create_app()
    debug = app.config.get('DEBUG', False)
    app.run(debug=debug, host=app.config.get('BIND_ADDRESS', '127.0.0.1'), port=app.config.get('PORT', '9191'))
