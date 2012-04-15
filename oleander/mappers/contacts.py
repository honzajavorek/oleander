# -*- coding: utf-8 -*-


from datetime import datetime
from . import Mapper


class ContactsMapper(Mapper):

    def from_csv_file(self, data):
        for row in data:
            try:
                parsed_bday_datetime = datetime.strptime(row.get('Birthday', ''), '%d.%m.%Y')
                bday_date = parsed_bday_datetime.date()
            except ValueError:
                bday_date = None

            first_name = row.get('First Name', None)
            middle_name = row.get('Middle Name', None)
            last_name = row.get('Last Name', None)

            name = row.get('Name', None)
            if not name:
                name = ' '.join([first_name, middle_name, last_name])

            yield self.create_entity(
                name=name,
                first_name=first_name,
                middle_name=middle_name,
                last_name=last_name,
                gender=row.get('Gender', None),
                birthday=bday_date,
                location=row.get('Location', None),
                language=row.get('Language', None),
                website=row.get('Web Page', None),
                email=row.get('E-mail Address', None),
                phone=row.get('Primary Phone', None),
                address=row.get('Primary Phone', None),
            )

