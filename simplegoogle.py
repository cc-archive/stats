import google
import time  # wish I didn't have to do this!
google.setLicense('oaiAhUtQFHIBLkPQ25A5u+EOItzW0PaK')
# The main reason for this module is that the Google SOAP API has an
# opaque "restrict" parameter.
# This should make it easier to deal with.



licenses = ['cc_publicdomain', 'cc_attribute', 'cc_sharealike', 'cc_noncommercial', 'cc_nonderived']
languages = {'Swedish': 'lang_sv', 'Icelandic': 'lang_is', 'Estonian': 'lang_et', 'Chinese (T)': 'lang_zh-TW', 'Romanian': 'lang_ro', 'English': 'lang_en', 'Dutch': 'lang_nl', 'Korean': 'lang_ko', 'Danish': 'lang_da', 'Hungarian': 'lang_hu', 'Turkish': 'lang_tr', 'French': 'lang_fr', 'Norwegian': 'lang_no', 'Russian': 'lang_ru', 'Finnish': 'lang_fi', 'Hebrew': 'lang_iw', 'Greek': 'lang_el', 'Latvian': 'lang_lv', 'Polish': 'lang_pl', 'Italian': 'lang_it', 'Portuguese': 'lang_pt', 'Czech': 'lang_cs', 'Japanese': 'lang_ja', 'German': 'lang_de', 'Chinese (S)': 'lang_zh-CN', 'Spanish': 'lang_es', 'Lithuanian': 'lang_lt', 'Arabic': 'lang_ar'}
countries = {'Canada': 'countryCA', 'Libyan Arab Jamahiriya': 'countryLY', 'Sao Tome and Principe': 'countryST', 'Turkmenistan': 'countryTM', 'Monaco': 'countryMC', 'Lithuania': 'countryLT', 'Bahamas': 'countryBS', 'Saint Kitts and Nevis': 'countryKN', 'Ethiopia': 'countryET', 'Aruba': 'countryAW', 'Swaziland': 'countrySZ', 'Svalbard and Jan Mayen Islands': 'countrySJ', 'Palestine': 'countryPS', 'Argentina': 'countryAR', 'Bolivia': 'countryBO', 'Cameroon': 'countryCM', 'Burkina Faso': 'countryBF', 'Bahrain': 'countryBH', 'Saudi Arabia': 'countrySA', 'Rwanda': 'countryRW', 'Togo': 'countryTG', 'Japan': 'countryJP', 'Cape Verde': 'countryCV', 'United States Minor Outlying Islands': 'countryUM', 'Cocos (Keeling) Islands': 'countryCC', 'Pitcairn': 'countryPN', 'Guatemala': 'countryGT', 'Kuwait': 'countryKW', 'Russian Federation': 'countryRU', 'Germany': 'countryDE', 'Taiwan': 'countryTW', 'Spain': 'countryES', 'Liberia': 'countryLR', 'Maldives': 'countryMV', 'Armenia': 'countryAM', 'Pakistan': 'countryPK', 'Oman': 'countryOM', 'Tanzania': 'countryTZ', 'Martinique': 'countryMQ', 'Macedonia, The Former Yugoslav Republic of': 'countryMK', 'Christmas Island': 'countryCX', 'Gabon': 'countryGA', 'Cambodia': 'countryKH', 'France, Metropolitan': 'countryFX', 'New Zealand': 'countryNZ', 'Yemen': 'countryYE', 'European Union': 'countryEU', 'Jamaica': 'countryJM', 'Albania': 'countryAL', 'Samoa': 'countryWS', 'Macau': 'countryMO', 'Norfolk Island': 'countryNF', 'United Arab Emirates': 'countryAE', 'Guam': 'countryGU', 'India': 'countryIN', 'Azerbaijan': 'countryAZ', 'Lesotho': 'countryLS', 'Saint Vincent and the Grenadines': 'countryVC', 'Bosnia and Herzegowina': 'countryBA', 'Kenya': 'countryKE', 'Tajikistan': 'countryTJ', 'Turkey': 'countryTR', 'Afghanistan': 'countryAF', 'Virgin Islands (British)': 'countryVG', 'Czech Republic': 'countryCZ', 'Mauritania': 'countryMR', 'Iran (Islamic Republic of)': 'countryIR', 'Turks and Caicos Islands': 'countryTC', 'Saint Lucia': 'countryLC', 'San Marino': 'countrySM', 'Mongolia': 'countryMN', 'France': 'countryFR', 'Luxembourg': 'countryLU', 'Bermuda': 'countryBM', 'Somalia': 'countrySO', 'Peru': 'countryPE', 'Vanuatu': 'countryVU', 'Nauru': 'countryNR', 'Seychelles': 'countrySC', 'Norway': 'countryNO', 'Malawi': 'countryMW', 'Cook Islands': 'countryCK', 'Benin': 'countryBJ', 'Cuba': 'countryCU', 'Falkland Islands (Malvinas)': 'countryFK', 'Mayotte': 'countryYT', 'Holy See (Vatican City State)': 'countryVA', 'China': 'countryCN', 'Micronesia, Federated States of': 'countryFM', 'Dominican Republic': 'countryDO', 'Ukraine': 'countryUA', 'Ghana': 'countryGH', 'Tonga': 'countryTO', 'Indonesia': 'countryID', 'Western Sahara': 'countryEH', 'St. Helena': 'countrySH', 'Finland': 'countryFI', 'Central African Republic': 'countryCF', 'Mauritius': 'countryMU', 'Liechtenstein': 'countryLI', 'Belarus': 'countryBY', 'Mali': 'countryML', 'East Timor': 'countryTP', 'Slovakia (Slovak Republic)': 'countrySK', 'Bulgaria': 'countryBG', 'United States': 'countryUS', 'Romania': 'countryRO', 'Angola': 'countryAO', 'French Southern Territories': 'countryTF', 'Cayman Islands': 'countryKY', 'South Africa': 'countryZA', 'Tokelau': 'countryTK', 'Cyprus': 'countryCY', 'South Georgia and the South Sandwich Islands': 'countryGS', 'Brunei Darussalam': 'countryBN', 'Qatar': 'countryQA', 'Malaysia': 'countryMY', 'Austria': 'countryAT', 'Vietnam': 'countryVN', 'Mozambique': 'countryMZ', 'Slovenia': 'countrySI', 'Uganda': 'countryUG', 'Hungary': 'countryHU', 'Niger': 'countryNE', 'Brazil': 'countryBR', 'Virgin Islands (U.S.)': 'countryVI', 'Faroe Islands': 'countryFO', 'Guinea': 'countryGN', 'Panama': 'countryPA', 'Korea, Republic of': 'countryKR', 'Costa Rica': 'countryCR', 'Morocco': 'countryMA', 'American Samoa': 'countryAS', 'Andorra': 'countryAD', 'Gibraltar': 'countryGI', 'Ireland': 'countryIE', 'Palau': 'countryPW', 'Nigeria': 'countryNG', 'Ecuador': 'countryEC', 'Bangladesh': 'countryBD', 'Australia': 'countryAU', 'Algeria': 'countryDZ', "Korea, Democratic People's Republic of": 'countryKP', 'El Salvador': 'countrySV', 'Tuvalu': 'countryTV', 'Solomon Islands': 'countrySB', 'Marshall Islands': 'countryMH', 'Chile': 'countryCL', 'Puerto Rico': 'countryPR', 'Belgium': 'countryBE', 'Kiribati': 'countryKI', 'Haiti': 'countryHT', 'Belize': 'countryBZ', 'Hong Kong': 'countryHK', 'Sierra Leone': 'countrySL', 'Georgia': 'countryGE', "Lao People's Democratic Republic": 'countryLA', 'Mexico': 'countryMX', 'Gambia': 'countryGM', 'Philippines': 'countryPH', 'Moldova': 'countryMD', 'Portugal': 'countryPT', 'Netherlands Antilles': 'countryAN', 'Namibia': 'countryNA', 'French Polynesia': 'countryPF', 'Guinea-Bissau': 'countryGW', 'Thailand': 'countryTH', 'Switzerland': 'countryCH', 'Grenada': 'countryGD', 'Wallis and Futuna Islands': 'countryWF', "Cote D'ivoire": 'countryCI', 'French Quiana': 'countryGF', 'Iraq': 'countryIQ', 'Chad': 'countryTD', 'Estonia': 'countryEE', 'Uruguay': 'countryUY', 'Sweden': 'countrySE', 'Bouvet Island': 'countryBV', 'Lebanon': 'countryLB', 'Uzbekistan': 'countryUZ', 'Tunisia': 'countryTN', 'Djibouti': 'countryDJ', 'Greenland': 'countryGL', 'Antigua and Barbuda': 'countryAG', 'Dominica': 'countryDM', 'Colombia': 'countryCO', 'Reunion': 'countryRE', 'Burundi': 'countryBI', 'Zaire': 'countryZR', 'Fiji': 'countryFJ', 'Barbados': 'countryBB', 'Madagascar': 'countryMG', 'Italy': 'countryIT', 'Bhutan': 'countryBT', 'Sudan': 'countrySD', 'Paraguay': 'countryPY', 'Nepal': 'countryNP', 'Malta': 'countryMT', 'Netherlands': 'countryNL', 'Northern Mariana Islands': 'countryMP', 'Suriname': 'countrySR', 'Anguilla': 'countryAI', 'Venezuela': 'countryVE', 'Israel': 'countryIL', 'St. Pierre and Miquelon': 'countryPM', 'Iceland': 'countryIS', 'Zambia': 'countryZM', 'Senegal': 'countrySN', 'Papua New Guinea': 'countryPG', 'Jordan': 'countryJO', 'Denmark': 'countryDK', 'Kazakhstan': 'countryKZ', 'Poland': 'countryPL', 'Croatia (local name: Hrvatska)': 'countryHR', 'Eritrea': 'countryER', 'Kyrgyzstan': 'countryKG', 'Congo, The Democratic Republic of the': 'countryCD', 'British Indian Ocean Territory': 'countryIO', 'Montserrat': 'countryMS', 'New Caledonia': 'countryNC', 'Heard and Mc Donald Islands': 'countryHM', 'Trinidad and Tobago': 'countryTT', 'Latvia': 'countryLV', 'Guyana': 'countryGY', 'Syria': 'countrySY', 'Guadeloupe': 'countryGP', 'Honduras': 'countryHN', 'Myanmar': 'countryMM', 'Equatorial Guinea': 'countryGQ', 'Egypt': 'countryEG', 'Nicaragua': 'countryNI', 'Singapore': 'countrySG', 'Comoros': 'countryKM', 'United Kingdom': 'countryUK', 'Antarctica': 'countryAQ', 'Congo': 'countryCG', 'Yugoslavia': 'countryYU', 'Greece': 'countryGR', 'Sri Lanka': 'countryLK', 'Botswana': 'countryBW', 'Niue': 'countryNU'}

def search(query, cc_spec=[], country=None, language=None):
    ''' cc_spec is a list of things this module knows about.
    country is a key in the countries list.
    language is a key in the languages list.
    They all get ANDed together at the last minute.'''
    for cc_thing in cc_spec: assert(cc_thing in licenses)
    restrict = cc_spec[:]
    if country:
        restrict.append(countries[country])
    if language:
        restrict.append(languages[language])

    retries = 0
    while retries < 1:
        try:
            result = google.doGoogleSearch(query,restrict='.'.join(restrict))
        except Exception, e:
            print e
            retries += 1
            sleeptime = retries * 2
            print "sleeping for", sleeptime
            time.sleep(sleeptime) # sleeping, assume API is acting up
    return result

def count(query, cc_spec=[], country=None, language=None):
    if country and language:
         print 'eek'
         country = None
    result = None # search(query, cc_spec, country, language)
    return result.meta.estimatedTotalResultsCount
