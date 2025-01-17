import json
from django.core.management.base import BaseCommand

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import FieldDoesNotExist
from django.db import connection

from TWLight.applications.models import Application
from TWLight.resources.models import (
    Partner,
    Stream,
    PartnerLogo,
    Contact,
    Video,
)
from TWLight.users.models import Authorization


class Command(BaseCommand):
    def handle(self, *args, **options):
        # Get Future Science Group streams
        future_science_streams = Stream.objects.filter(
            partner__company_name__contains="Future Science Group"
        )

        # Get RILM streams
        rilm_streams = Stream.objects.filter(
            partner__company_name__contains="Répertoire International de Littérature Musicale (RILM)"
        )

        # Get Springer Nature streams
        springer_nature_streams = Stream.objects.filter(
            partner__company_name__contains="Springer Nature"
        )

        future_science_stream_and_partner_ids = self._turn_stream_to_partner(
            future_science_streams
        )
        rilm_stream_and_partner_ids = self._turn_stream_to_partner(rilm_streams)
        springer_nature_stream_and_partner_ids = self._turn_stream_to_partner(
            springer_nature_streams
        )

        self._create_descriptions(
            future_science_stream_and_partner_ids,
            rilm_stream_and_partner_ids,
            springer_nature_stream_and_partner_ids,
        )

        self._assign_applications_to_new_partners(future_science_stream_and_partner_ids)
        self._assign_applications_to_new_partners(rilm_stream_and_partner_ids)
        self._assign_applications_to_new_partners(
            springer_nature_stream_and_partner_ids
        )

        self._assign_authorizations_to_new_partners(
            future_science_stream_and_partner_ids
        )
        self._assign_authorizations_to_new_partners(rilm_stream_and_partner_ids)
        self._assign_authorizations_to_new_partners(
            springer_nature_stream_and_partner_ids
        )

        # Once applications and authorizations are reassigned, we can safely
        # delete the streams
        future_science_streams.delete()
        rilm_streams.delete()
        springer_nature_streams.delete()

        # Once streams are deleted, we can safely delete the partners

        # Get Future Science Group partner
        future_science_partner = Partner.objects.filter(pk=22).first()

        # Get RILM partner
        rilm_partner = Partner.objects.filter(pk=100).first()

        # Get Springer Nature partner
        springer_nature_partner = Partner.objects.filter(pk=67).first()

        future_science_partner.delete()
        rilm_partner.delete()
        springer_nature_partner.delete()

    def _turn_stream_to_partner(self, streams):
        """
        Function that creates a partner out of a series of streams
        ----------
        streams : Queryset<Stream>
            The streams that need to be turned into partners

        Returns
        -------
        dict
            A dictionary with the stream ID and the new partner ID that was created
            from that stream's information
        """
        stream_and_partner_ids = []

        for stream in streams:
            stream_partner_information = {}

            stream_partner_information[
                "company_name"
            ] = "{partner_name} - {stream_name}".format(
                partner_name=stream.partner.company_name, stream_name=stream.name
            )

            if stream.partner.coordinator:
                stream_partner_information["coordinator"] = stream.partner.coordinator

            stream_partner_information["featured"] = stream.partner.featured
            stream_partner_information[
                "company_location"
            ] = stream.partner.company_location
            stream_partner_information["status"] = stream.partner.status
            stream_partner_information[
                "renewals_available"
            ] = stream.partner.renewals_available
            stream_partner_information["accounts_available"] = stream.accounts_available
            stream_partner_information["target_url"] = stream.target_url
            stream_partner_information["terms_of_use"] = stream.partner.terms_of_use
            stream_partner_information[
                "send_instructions"
            ] = stream.partner.send_instructions
            stream_partner_information["user_instructions"] = stream.user_instructions
            stream_partner_information["excerpt_limit"] = stream.partner.excerpt_limit
            stream_partner_information[
                "excerpt_limit_percentage"
            ] = stream.partner.excerpt_limit_percentage
            stream_partner_information[
                "authorization_method"
            ] = stream.authorization_method
            stream_partner_information[
                "mutually_exclusive"
            ] = stream.partner.mutually_exclusive

            stream_partner_information["account_length"] = stream.partner.account_length
            stream_partner_information["new_tags"] = stream.partner.new_tags
            stream_partner_information[
                "registration_url"
            ] = stream.partner.registration_url
            stream_partner_information["real_name"] = stream.partner.real_name
            stream_partner_information[
                "country_of_residence"
            ] = stream.partner.country_of_residence
            stream_partner_information["specific_title"] = stream.partner.specific_title
            stream_partner_information["occupation"] = stream.partner.occupation
            stream_partner_information["affiliation"] = stream.partner.affiliation
            stream_partner_information[
                "agreement_with_terms_of_use"
            ] = stream.partner.agreement_with_terms_of_use
            stream_partner_information["account_email"] = stream.partner.account_email
            stream_partner_information[
                "requested_access_duration"
            ] = stream.partner.requested_access_duration

            partner_check = Partner.objects.filter(
                company_name=stream_partner_information["company_name"]
            ).count()

            if partner_check == 0:
                new_partner = Partner.objects.create(**stream_partner_information)

                if stream.languages.all():
                    new_partner.languages.set(stream.languages.all())
                elif stream.partner.languages.all():
                    new_partner.languages.set(stream.partner.languages.all())

                stream_and_partner_ids.append(
                    {"stream_id": stream.pk, "partner_id": new_partner.pk}
                )

        return stream_and_partner_ids

    def _create_descriptions(
        self,
        future_science_stream_and_partner_ids,
        rilm_stream_and_partner_ids,
        springer_nature_stream_and_partner_ids,
    ):
        """
        Function that calls on other functions to create a partner's description
        ----------
        future_science_stream_and_partner_ids : dict
            A dictionary that contains the original stream ID and the newly created partner ID
        rilm_stream_and_partner_ids : dict
            A dictionary that contains the original stream ID and the newly created partner ID
        springer_nature_stream_and_partner_ids : dict
            A dictionary that contains the original stream ID and the newly created partner ID

        Returns
        -------
        None
        """
        future_science_descriptions = self._add_stream_descriptions(
            future_science_stream_and_partner_ids
        )
        rilm_descriptions = self._add_stream_descriptions(rilm_stream_and_partner_ids)
        springer_nature_descriptions = self._add_stream_descriptions(
            springer_nature_stream_and_partner_ids
        )

        descriptions_dict = self._merge_dictionaries(
            future_science_descriptions,
            rilm_descriptions,
            springer_nature_descriptions,
        )

        self._write_descriptions_file(descriptions_dict)

    def _add_stream_descriptions(self, stream_and_partner_ids):
        """
        Function that creates a dictionary from stream descriptions
        ----------
        stream_and_partner_ids : dict
            A dictionary that contains the original stream ID and the newly created partner ID

        Returns
        -------
        dict
            A dictionary with stream descriptions
        """
        stream_descriptions = {}
        language_codes = [l[0] for l in settings.LANGUAGES]
        for stream_and_partner_id in stream_and_partner_ids:
            stream = Stream.objects.filter(
                pk=stream_and_partner_id["stream_id"]
            ).first()

            if stream:
                for language in language_codes:
                    description_string = "description_{locale}".format(locale=language)
                    # Check if a field description_locale exists
                    try:
                        description_object = Stream._meta.get_field(description_string)
                        description_value = description_object.value_from_object(stream)
                    except FieldDoesNotExist:
                        description_value = ""

                    if description_value != "" or description_value is not None:
                        stream_description_key = (
                            "{partner_id}_description_{language}".format(
                                partner_id=stream_and_partner_id["partner_id"],
                                language=language,
                            )
                        )
                        stream_descriptions[stream_description_key] = description_value

        return stream_descriptions

    def _merge_dictionaries(self, *args):
        output = {}
        for arg in args:
            output.update(arg)
        return output

    def _write_descriptions_file(self, descriptions_dict):
        """
        Function that creates a dictionary from stream descriptions
        ----------
        descriptions_dict : dict
            A dictionary with all stream descriptions

        Returns
        -------
        None
        """
        twlight_home = settings.TWLIGHT_HOME
        filename = "{twlight_home}/temp_stream_descriptions.json".format(
            twlight_home=twlight_home,
        )
        with open(filename, "w") as descriptions_file:
            descriptions_file.write(json.dumps(descriptions_dict, indent=4))

    def _assign_applications_to_new_partners(self, stream_and_partner_ids):
        """
        Function that reassigns applications to the newly created partners
        ----------
        stream_and_partner_ids : dict
            A dictionary that contains the original stream ID and the newly created partner ID

        Returns
        -------
        None
        """
        # Some applicartions have Jason's personal account in the sent_by
        # field. Since that account is no longer staff, we will replace it
        # with Jason's WMF account
        jsn_sherman = User.objects.get(username=49305455)
        j_sherman = User.objects.get(username=49828274)
        for stream_and_partner_id in stream_and_partner_ids:
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE applications_application SET partner_id = %s, specific_stream_id = NULL WHERE specific_stream_id = %s AND sent_by_id != %s",
                    [
                        stream_and_partner_id["partner_id"],
                        stream_and_partner_id["stream_id"],
                        jsn_sherman.pk,
                    ],
                )
                cursor.execute(
                    "UPDATE applications_application SET partner_id = %s, specific_stream_id = NULL, sent_by_id = %s WHERE specific_stream_id = %s AND sent_by_id = %s",
                    [
                        stream_and_partner_id["partner_id"],
                        j_sherman.pk,
                        stream_and_partner_id["stream_id"],
                        jsn_sherman.pk,
                    ],
                )

    def _assign_authorizations_to_new_partners(self, stream_and_partner_ids):
        """
        Function that reassigns authorizations to the newly created partners
        ----------
        stream_and_partner_ids : dict
            A dictionary that contains the original stream ID and the newly created partner ID

        Returns
        -------
        None
        """
        # Some applicartions have Jason's personal account in the sent_by
        # field. Since that account is no longer staff, we will replace it
        # with Jason's WMF account
        jsn_sherman = User.objects.get(username=49305455)
        j_sherman = User.objects.get(username=49828274)
        for stream_and_partner_id in stream_and_partner_ids:
            authorizations = Authorization.objects.filter(
                stream=stream_and_partner_id["stream_id"]
            )
            for authorization in authorizations:
                with connection.cursor() as cursor:
                    cursor.execute(
                        "UPDATE users_authorization_partners SET partner_id = %s WHERE authorization_id = %s",
                        [
                            stream_and_partner_id["partner_id"],
                            authorization.pk,
                        ],
                    )
            with connection.cursor() as cursor:
                cursor.execute(
                    "UPDATE users_authorization SET stream_id = NULL WHERE stream_id = %s AND authorizer_id != %s",
                    [
                        stream_and_partner_id["stream_id"],
                        jsn_sherman.pk,
                    ],
                )
                cursor.execute(
                    "UPDATE users_authorization SET stream_id = NULL, authorizer_id = %s WHERE stream_id = %s AND authorizer_id = %s",
                    [
                        j_sherman.pk,
                        stream_and_partner_id["stream_id"],
                        jsn_sherman.pk,
                    ],
                )
