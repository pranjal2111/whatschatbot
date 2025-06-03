from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from twilio.twiml.messaging_response import MessagingResponse
from .models import MessageLog


@csrf_exempt
def home(request):
    return HttpResponse("✅ WhatsApp Bot is Running. Use POST at /whatsapp_reply")


@csrf_exempt
def whatsapp_reply(request):
    if request.method == 'POST':
        incoming_msg = request.POST.get('Body', '').strip()
        sender = request.POST.get('From', '').replace('whatsapp:', '')
        MessageLog.objects.create(sender=sender, body=incoming_msg)

        resp = MessagingResponse()
        msg = resp.message()

        text = incoming_msg.strip().lower()  # normalize input for easier matching

        # Define all valid commands with possible variations (gujarati, english, upper, lower)
        commands_map = {
            # Main menu triggers
            ("hi", "menu", "મેનુ", "નમસ્તે"): "📋 MAIN MENU:\n"
                                              "- For Non-Anamat Certificate\n"
                                              "- For Widow Assistance\n"
                                              "- For Income Certificate\n"
                                              "- For Vhali Dikri\n"
                                              "- For R.T.E\n"
                                              "- For EBC/EWS / 10% Reservation\n"
                                              "- For Old Age Assistance\n"
                                              "- For Guardian Mother/Father\n"
                                              "- For Inheritance Documents\n"
                                              "- For 7/12/8-A Land Records\n"
                                              "- For Kunvarbai's Mamru\n"
                                              "- For Non-Criminal Record\n"
                                              "- For Caste Certificate\n"
                                              "- For SatyaVadi Raja Harishchandra Scheme\n"
                                              "- For Marriage Registration\n"
                                              "- For Scholarship Forms\n\n"
                                              "Reply with the exact option name.",

            ("બિન અનામત દાખલા માટે", "non-anamat certificate", "NON-ANAMAT CERTIFICATE", "non-anamat certificate"):
                "📄 For Non-Anamat Certificate:\n"
                "- Xerox of Coupon\n"
                "- Xerox of Aadhaar Card\n"
                "- Xerox of Light Bill\n"
                "- Tax Receipt\n"
                "- 1 Photo\n"
                "- Xerox of Applicant's School Leaving Certificate\n"
                "- Xerox of Father/Uncle/Relative's School Leaving Certificate\n"
                "- Domicile Certificate\n"
                "- 1 Photo of Father\n"
                "- Xerox of Father's Aadhaar Card\n"
                "- Xerox of Father's School Leaving Certificate\n"
                "- Police Station Certificate\n"
                "- Birth Certificate\n"
                "- Income Certificate\n"
                "- Marksheet from 1st Standard till Last",

            ("વિધવા સહાય માટે", "widow assistance", "WIDOW ASSISTANCE", "widow assistance"):
                "📄 For Widow Assistance:\n"
                "- Xerox of Coupon\n"
                "- Xerox of Aadhaar Card\n"
                "- Xerox of Income Certificate\n"
                "- Age Proof (Birth Certificate / School Leaving Certificate / Govt. Hospital Certificate)\n"
                "- Xerox of Light Bill\n"
                "- 4 Photos\n"
                "- Bank Passbook\n"
                "- Tax Receipt\n"
                "- Xerox of Husband's Death Certificate\n"
                "- Xerox of All Family Members' Aadhaar Card\n"
                "- Xerox of Coupon and Income Certificates of all family members",

            ("આવક દાખલા માટે", "income certificate", "INCOME CERTIFICATE", "income certificate"):
                "📄 For Income Certificate:\n"
                "- Xerox of Coupon\n"
                "- 1 Photo\n"
                "- Xerox of Aadhaar Card\n"
                "- Xerox of Election Card\n"
                "- Tax Receipt\n"
                "- Xerox of Light Bill",

            ("વ્હાલી દિકરી માટે", "vhali dikri", "VHALI DIKRI", "vhali dikri"):
                "📄 For Vhali Dikri:\n"
                "- Birth Certificate and Aadhaar Card of Child\n"
                "- Photo of Child\n"
                "- Marriage Certificate of Parents\n"
                "- Xerox of Parents' School Leaving Certificate\n"
                "- Xerox of Parents' Coupon\n"
                "- Xerox of Parents' Aadhaar Card\n"
                "- Father's Income Certificate\n"
                "- Bank Passbook of Mother or Father\n"
                "- Birth Certificate and Aadhaar Card of Older Children",

            ("આર.ટી.ઇ.", "rte", "RTE", "rte"):
                "📄 For R.T.E:\n"
                "- Child's Birth Certificate\n"
                "- Child's Aadhaar Card\n"
                "- Child's Photo\n"
                "- Coupon\n"
                "- Parents' Aadhaar Cards\n"
                "- Father's Income Certificate\n"
                "- Bank Passbook\n"
                "- B.P.L. Card (if any)\n"
                "- PAN Card\n"
                "- Caste Certificate (if applicable)",

            ("ebc/ews / 10% અનામત", "ebc/ews / 10% reservation", "EBC/EWS / 10% RESERVATION",
             "ebc/ews / 10% reservation"):
                "📄 For EBC/EWS / 10% Reservation:\n"
                "- Xerox of Coupon\n"
                "- Xerox of Aadhaar Card\n"
                "- Xerox of Light Bill\n"
                "- Tax Receipt\n"
                "- 1 Photo\n"
                "- Father's/Husband's Income Certificate\n"
                "- 1 Photo of Father\n"
                "- Xerox of Father's Aadhaar Card\n"
                "- Xerox of Applicant's School Leaving Certificate\n"
                "- Xerox of Father/Uncle/Relative's School Leaving Certificate",

            ("વ્રુધ્ધ સહાય", "old age assistance", "OLD AGE ASSISTANCE", "old age assistance"):
                "📄 For Old Age Assistance:\n"
                "- Xerox of Coupon\n"
                "- Xerox of Aadhaar Card\n"
                "- Age Proof (Birth Certificate / School Leaving Certificate / Govt. Hospital Certificate)\n"
                "- Bank Passbook\n"
                "- B.P.L Card or B.P.L Certificate\n"
                "- 1 Photo",

            ("પાલક માતા પીતા", "guardian mother father", "GUARDIAN MOTHER FATHER", "guardian mother father"):
                "📄 For Guardian Mother/Father:\n"
                "- Child's Birth Certificate\n"
                "- Xerox of Child's Aadhaar Card\n"
                "- Child's School Bonafide Certificate\n"
                "- Death Certificate and Aadhaar Card of Child's Parents\n"
                "- Single Photo of Child\n"
                "- Photo of Child with Guardian Mother/Father\n"
                "- Bank Passbook of Child with Guardian Mother/Father\n"
                "- Xerox of Guardian Mother/Father's Coupon\n"
                "- Xerox of Guardian Mother/Father's Aadhaar Card\n"
                "- Guardian Father's Income Certificate\n"
                "- Xerox of Light Bill",

            ("વારસાઈ આંબો બનાવવા માટે", "for inheritance documents", "FOR INHERITANCE DOCUMENTS",
             "for inheritance documents"):
                "📄 For Inheritance Documents:\n"
                "- Affidavit of Declarant\n"
                "- Xerox of Coupon\n"
                "- Xerox of Aadhaar Card\n"
                "- Death Certificate\n"
                "- 1 Photo\n"
                "- Xerox of Aadhaar Cards of All Heirs",

            ("૭/ ૧૨ / ૮ –અ માં વારસાઈ માટે", "7/12/8-a inheritance", "7/12/8-A INHERITANCE", "7/12/8-a inheritance"):
                "📄 For 7/12/8-A Inheritance:\n"
                "- 7/12 Land Record\n"
                "- Vari Ticket\n"
                "- Death Certificate\n"
                "- Aadhaar Card of Heirs\n"
                "- Coupons of All Categories",

            ("કુંવરબાઈનું મામેરું", "kunvarbai's mamru", "KUNVARBAI'S MAMRU", "kunvarbai's mamru"):
                "📄 For Kunvarbai's Mamru:\n"
                "- Marriage Certificate\n"
                "- Birth Certificate\n"
                "- Aadhaar Card\n"
                "- Coupon\n"
                "- 1 Photo\n"
                "- Other Relevant Documents",

            ("non crimileyar", "non criminal record", "NON CRIMINAL RECORD", "non criminal record"):
                "📄 For Non Criminal Record:\n"
                "- Official Court Verification\n"
                "- Police Station Certificate\n"
                "- Aadhaar Card\n"
                "- 1 Photo",

            ("જાતી દાખલો", "caste certificate", "CASTE CERTIFICATE", "caste certificate"):
                "📄 For Caste Certificate:\n"
                "- Relevant Caste Certificate\n"
                "- Aadhaar Card\n"
                "- Income Certificate\n"
                "- 1 Photo",

            ("સત્યવાદી રાજા હરીશચંદ્ર મરણોતર સહાય યોજના", "satyavadi raja harishchandra death assistance scheme",
             "SATYAVADI RAJA HARISHCHANDRA DEATH ASSISTANCE SCHEME",
             "satyavadi raja harishchandra death assistance scheme"):
                "📄 For Satyavadi Raja Harishchandra Death Assistance Scheme:\n"
                "- Death Certificate\n"
                "- Applicant's Aadhaar Card\n"
                "- Income Certificate\n"
                "- 2 Photos\n"
                "- Death Certificate of Husband/Wife",

            ("લગ્ન નોંધણી માટે", "marriage registration", "MARRIAGE REGISTRATION", "marriage registration"):
                "📄 For Marriage Registration:\n"
                "- Aadhaar Cards of Both Parties\n"
                "- Two Photos Each\n"
                "- Documents Regarding Consent\n"
                "- Marriage Certificate (if any)\n"
                "- Marriage Place and Date",

            ("સ્કોલરશીપના ફોર્મ માટે", "scholarship forms", "SCHOLARSHIP FORMS", "scholarship forms"):
                "📄 For Scholarship Forms:\n"
                "- Student's Aadhaar Card\n"
                "- Birth Certificate\n"
                "- Study Certificate\n"
                "- Parents' Income Certificates\n"
                "- 2 Photos\n"
                "- Bank Passbook",
        }

        # Check input against keys (all converted to lowercase)
        matched = False
        for keys, reply in commands_map.items():
            if text in [k.lower() for k in keys]:
                msg.body(reply)
                matched = True
                break

        if not matched:
            msg.body(
                "Sorry, I didn't understand your command.\n"
                "Type 'menu' to see the options."
            )

        return HttpResponse(str(resp), content_type='application/xml')
    else:
        return HttpResponse("Only POST requests are accepted", status=405)
