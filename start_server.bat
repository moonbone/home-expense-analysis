pushd expense_site

call workon test

python manage.py runserver 0:8000



popd
pause
