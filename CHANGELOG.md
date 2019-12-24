### 1.5.3
- Fix PGT lookup during proxy authentication (https://github.com/kstateome/django-cas/pull/84)
- Fix CASBackend test (https://github.com/kstateome/django-cas/pull/86)

### 1.5.2
- Fix gateway feature (https://github.com/kstateome/django-cas/pull/91)

### 1.5.1
- Include request in authenticate and evaluate gateway query_list (https://github.com/kstateome/django-cas/pull/87)

### 1.5.0
- Path Change (https://github.com/kstateome/django-cas/pull/76)
- Update authenticate method (https://github.com/kstateome/django-cas/pull/77/files)

### 1.4.0
- Compatibility with Django 2.0 (https://github.com/kstateome/django-cas/pull/72)

### 1.3.0
- Compatibility with Django 1.10 Middleware (https://github.com/kstateome/django-cas/pull/69)
- Add support for protocol-rooted URL as "next_page" argument for _logout_url constructor (https://github.com/kstateome/django-cas/pull/67)
- Fix typo (https://github.com/kstateome/django-cas/pull/65)

### 1.2.0

- Allow opt out of time delay caused by fetching PGT tickets
- Add support for gateway not returning a response
- Allow forcing service URL over HTTPS (https://github.com/kstateome/django-cas/pull/48)
- Allow user creation on first login to be optional (https://github.com/kstateome/django-cas/pull/49)

### 1.1.1

- Add a few logging statements
- Add official change log.
