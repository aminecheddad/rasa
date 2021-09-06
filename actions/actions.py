# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from requests import NullHandler

from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import AllSlotsReset
import mysql.connector
from rasa_sdk.executor import CollectingDispatcher
import json 
import requests
from urllib.parse import urljoin
import urllib.request
import urllib.error
import urllib
import json
import time

class QueryLabs(Action):

    def name(self) -> Text:
        return "query_labs"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #connect to the database 
        connection = connect_db("sql4.freemysqlhosting.net", "sql4434818", "jp9sSCva1f", "sql4434818")
        #get the value 
        value = tracker.get_slot("lab_name")
        #select data
        get_query_results = select_from_where_one(connection, "labs", "acronyme", value)

        dispatcher.utter_message(text=format_labs_output(get_query_results))

        return []

class QueryProfs(Action):

    def name(self) -> Text:
        return "query_profs"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #connect to the database 
        connection = connect_db("sql4.freemysqlhosting.net", "sql4434818", "jp9sSCva1f", "sql4434818")
        #get the value 
        value = tracker.get_slot("dprt_name")
        #select data
        get_query_results = select_from_where(connection, "corps_professoral", "Departement", value)

        dispatcher.utter_message(text=format_faculty(get_query_results))

        return []

class ValidateAdmissionForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_admission_form"

    @staticmethod
    def formation_db() -> List[Text]:
        """Database of supported keys formation"""
        return ["master", "cycle"]

    @staticmethod
    def cursus_db() -> List[Text]:
        """Database of supported keys formation"""
        return ['deug', 'dut', 'deust', 'deup', 'licence', 'cpge']


    def validate_formation_type(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]: 

        """Validate formation_type value."""
        #force to give master or cycle key
        if value.lower() in self.formation_db(): 
            return {"formation_type": value}
        else :
            dispatcher.utter_message(text = standard_format("Le mot que vous avez donner est invalide veuillez dire 'cycle' ou 'master'"))
            return {"formation_type": None}

    def validate_cursus(
        self,
        value: Text,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> Dict[Text, Any]: 
        """Validate cursus value."""
        if value.lower() in self.cursus_db() :
            return {"cursus": value}
        else : 
            dispatcher.utter_message(text = standard_format("Le mot que vous avez donner est invalide veuillez dire 'deug', 'dut', 'deust', 'deup', 'licence', 'cpge'"))
            return {"cursus": None}

class AdmissionAnswer(Action):

    def name(self) -> Text:
        return "admission_answer"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #slots

        formation_slot = tracker.get_slot("formation_type")
        cursus = tracker.get_slot("cursus")
        print(formation_slot, cursus)

        if (formation_slot == "cycle") : 
            if(cursus == "cpge") : 
                dispatcher.utter_message(response="utter_cycle_cpge")
                return [AllSlotsReset()]
            else : 
                dispatcher.utter_message(response="utter_cycle_other")
                return [AllSlotsReset()]
        else : 
            if(cursus == "licence") :
                dispatcher.utter_message(response="utter_master_licence")
                return [AllSlotsReset()]
            else :
                dispatcher.utter_message(response="utter_master_other")
                return [AllSlotsReset()]


class QueryEvents(Action):

    def name(self) -> Text:
        return "query_events"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #connect to the database 
        connection = connect_db("sql4.freemysqlhosting.net", "sql4434818", "jp9sSCva1f", "sql4434818")
        #select data
        get_query_results = select_from_all(connection, "events")
        if (get_query_results) : 
            dispatcher.utter_message(text=events_format(get_query_results))
            return []
        else : 
            dispatcher.utter_message(text=standard_format("Oups, il n'y a aucun événement disponible, veuillez vous inscrire pour recevoir les dernières nouvelles et événements."))
            return []

class WeatherRequest(Action):

    def name(self) -> Text:
        return "weather_request"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        weather_data = get_weather()
        if weather_data == -1 : 
            msg = "Oops, une erreur est survenue veuillez reéssayer ultérieurement"
            dispatcher.utter_message(text=standard_format(msg))
            return []
        #if its good :)
        dispatcher.utter_message(text=weather_data)
        return []

class QueryNews(Action):

    def name(self) -> Text:
        return "query_news"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #connect to the database 
        connection = connect_db("sql4.freemysqlhosting.net", "sql4434818", "jp9sSCva1f", "sql4434818")
        #select data
        get_query_results = select_from_all(connection, "latest_news")
        if (get_query_results) : 
            dispatcher.utter_message(text=news_format(get_query_results))
            return []
        else : 
            dispatcher.utter_message(text=standard_format("Oups, rien de nouveau à partager, veuillez vous abonner pour recevoir les dernières nouvelles et événements."))
            return []


class QueryEng(Action):

    def name(self) -> Text:
        return "query_eng"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #connect to the database 
        connection = connect_db("sql4.freemysqlhosting.net", "sql4434818", "jp9sSCva1f", "sql4434818")
        #get the value 
        value = tracker.get_slot("field_name")
        print(value)
        if value in ["data science", "statistique démographie", "statistique economie", "data engineer", "actuariat finance"] : 
            output = select_from_where_one(connection, "program_ing", "program_title", value)
            dispatcher.utter_message(text=eng_fields_fone(output))
            return []
        output = select_from_all(connection, "program_ing")
        full_program_str = eng_fields_format(output)
        dispatcher.utter_message(text=full_program_str)
        return [] 

class QueryMaster(Action):

    def name(self) -> Text:
        return "query_master"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #connect to the database 
        connection = connect_db("sql4.freemysqlhosting.net", "sql4434818", "jp9sSCva1f", "sql4434818")
        #select data
        get_query_results = select_from_all(connection, "program_master")
        if (get_query_results) : 
            dispatcher.utter_message(text=master_format(get_query_results))
            return []
        else : 
            dispatcher.utter_message(text=standard_format("Oups, Il y a pas de programmes Master pour le moment, réessayez  ultérieurement..."))
            return []

class QueryPhd(Action):

    def name(self) -> Text:
        return "query_phd"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        #connect to the database 
        connection = connect_db("sql4.freemysqlhosting.net", "sql4434818", "jp9sSCva1f", "sql4434818")
        #select data
        get_query_results = select_from_all(connection, "program_phd")
        if (get_query_results) : 
            dispatcher.utter_message(text=phd_format(get_query_results))
            return []
        else : 
            dispatcher.utter_message(text=standard_format("Oups, Il y a pas de programmes Phd pour le moment, réessayez  ultérieurement..."))
            return []


class AskLabName(Action):

    def name(self) -> Text:
        return "ask_lab_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        buttons = [
            {"payload" : '/inform{"lab_name":"masafeq"}', "title" : "masafeq lab"}, 
            {"payload" : '/inform{"lab_name":"si2m"}', "title" : "si2m lab"} , 
            {"payload" : '/inform{"lab_name":"ges3d"}', "title" : "ges3d lab"}
        ]

        dispatcher.utter_message(text=generate_buttons("Veuillez sélectionner un nom de laboratoire :", buttons), buttons = buttons)

        return []

class AskFieldName(Action):

    def name(self) -> Text:
        return "ask_field_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        buttons = [
            {"payload" : '/inform{"field_name":"data science"}', "title" : "data science"}, 
            {"payload" : '/inform{"field_name":"statistique démographie"}', "title" : "statistique démographie"} , 
            {"payload" : '/inform{"field_name":"statistique économie"}', "title" : "statistique économie"},
            {"payload" : '/inform{"field_name":"actuariat finance"}', "title" : "actuariat finance"}, 
            {"payload" : '/inform{"field_name":"data engineer"}', "title" : "data engineer"} , 
            {"payload" : '/inform{"field_name":"recherche opérationnelle"}', "title" : "recherche opérationnelle"}
        ]

        dispatcher.utter_message(text=generate_buttons("Veuillez sélectionner une filière :", buttons), buttons = buttons)

        return []

class AskDprtName(Action):

    def name(self) -> Text:
        return "ask_dprt_name"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        buttons = [
            {"payload" : '/inform{"dprt_name":"informatique"}', "title" : "informatique"}, 
            {"payload" : '/inform{"dprt_name":"mathématique et recherche opérationnelle"}', "title" : "mathématique et recherche opérationnelle"} , 
            {"payload" : '/inform{"dprt_name":"science sociales"}', "title" : "sciences sociales"},
            {"payload" : '/inform{"dprt_name":"statistique démographie et actuariat"}', "title" : "statistique démographie et actuariat"}, 
            {"payload" : '/inform{"dprt_name":"economie et finance"}', "title" : "economie et finance"}
        ]

        dispatcher.utter_message(text=generate_buttons("Veuillez sélectionner un département pour obtenir les noms des professeurs :", buttons), buttons = buttons)

        return []

def standard_format(msg) : 
    standard_msg = """<div class = "bot_full_corps"><div class='d-flex flex-row p-3'><div class='w-100'><div class='d-flex justify-content-between align-items-center'><div class='d-flex flex-row align-items-center'></div></div><p class='bot_corps'>{content}</p><div class = 'is_useful' ><div class = 'is_useful_message' id = 'robot_answer_2'>Si la réponse n'est pas exacte, veuillezdouble-cliquer pour signaler</div><span class = "clicked" style = "display:none;">Merci</span></div></div></div></div>"""
    return standard_msg.format(content = msg)

def generate_buttons(msg, buttons_list):
    buttons_string = """
	<div class='d-flex flex-row p-3'>
		<div class='w-100'>
			<div class='d-flex justify-content-between align-items-center'>
				<div class='d-flex flex-row align-items-center'>
				</div>
			</div>
			<p class='bot_corps'>{}</p>
			<br />{}
			<div class = "is_useful" >
				<div class = "is_useful_message" id = "robot_answer_2">Si la réponse n'est pas exacte, veuillez double-cliquer pour signaler
				</div>
				<span class = "clicked" style = "display:none;">Merci</span>
			</div>
		</div>
	</div>"""
    one_button = """<a class='btn btn-primary btn-sm m-1' href = '?text={payload}'>{title}</a>"""
    buttons = []
    for button in buttons_list : 
        buttons.append(one_button.format_map(button))
    return buttons_string.format(msg, "".join(buttons)).replace("\n", "")


def get_weather() :
    weather = download_link("http://dataservice.accuweather.com/currentconditions/v1/245072?apikey=4BYTiKsOGa8t6Qwvhoxii096FpdXNWGR").read()
    if not (weather) :
        return -1
    json_weather = json.loads(weather)[0]
    card = """
    <div class='d-flex flex-row p-3'>
    <div class='w-100'>
    <p class = "bot_corps">voici la météo à Rabat, vous devriez penser à quoi porter avant de sortir !</p></div></div>
    <div class='card text-center' style='width: 18rem;'>
              <img class='card-img-top' src='https://developer.accuweather.com/sites/default/files/{WeatherIcon:02d}-s.png'>
              <div class='card-body'>
                <h1 class='card-title text-center' style = "font-family: 'Alegreya Sans ExtraBold', sans-serif;">{Temperature[Metric][Value]} {Temperature[Metric][Unit]}</h1>
                <p class='card-text text-center' style = "font-family: 'Alegreya Sans Light', sans-serif;">Rabat<br /> <p class = "div_time_ago text-center">{WeatherText}</p></p>
                <div class = 'is_useful' ><div class = 'is_useful_message' id = 'robot_answer_2'>Si la réponse n'est pas exacte, veuillezdouble-cliquer pour signaler</div><span class = "clicked" style = "display:none;">Merci</span></div>
              </div>
              </div>""".format_map(json_weather)
    return card

def download_link(link, attempts = 2) : 
    try : 
        data = urllib.request.urlopen(link)
        print("Link downloaded succesfully {}".format(link))
    except urllib.error.URLError as e : 
        print("An Error has occured while downloading the given link {}\n{}".format(link, e.reason))
        data = e.reason 
        if attempts>0 : 
            if hasattr(e, 'code') and 100 <= e.code <600 : #server error codes interval [500,600[
                print("Problème dans le serveur autre tentative dans 3 sec")
                time.sleep(3)
                download_link(link, attempts-1)
            else : 
                print("Nombre de tentatives dépassé !")
    return data

def phd_format(output) :
    active = """
            <div class="carousel-item active">
                <div class="card active" style="width: 18rem;">
                <div class="card-body text-center">
                    <h1 class="card-title text-center" style = "font-family: Alegreya Sans ExtraBold, sans-serif;">{intitulé}</h1>
                <div class="card-body text-center">
                    <a target="_blank" href  = "{charte}" target="_blank">Découvrir le charte</a><br />
                    <a target="_blank" href = "{réglements}" target="_blank">Voir les réglement</a>
                </div>
                </div>
                </div>
            </div>"""
    standard = """
            <div class="carousel-item">
                <div class="card" style="width: 18rem;">
                <div class="card-body text-center">
                    <h1 class="card-title text-center" style = "font-family: Alegreya Sans ExtraBold, sans-serif;">{intitulé}</h1>
                <div class="card-body text-center">
                    <a target="_blank" href = "{charte}" target="_blank">Découvrir le charte</a><br />
                    <a target="_blank" href = "{réglements}" target="_blank">Voir les réglement</a>
                </div>
                </div>
                </div>
            </div>"""
    active_dict = output[0]
    divs = [active.format_map(active_dict)]
    standard_elements = output[1:]
    for element in standard_elements : 
        divs.append(standard.format_map(element))
    full_div = """
	<div class='d-flex flex-row p-3'>
		<div class='w-100'>
			<div class='d-flex justify-content-between align-items-center'>
				<div class='d-flex flex-row align-items-center'>
				</div>
			</div>
                <div id="carouselExampleControls" class="carousel slide" data-ride="carousel">
        <div class="carousel-inner">
            {}
        </div>
        <a class="carousel-control-prev" href="#carouselExampleControls" role="button" data-slide="prev">
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="sr-only">Previous</span>
        </a>
        <a class="carousel-control-next" href="#carouselExampleControls" role="button" data-slide="next">
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="sr-only">Next</span>
        </a>
    </div>
			<div class = "is_useful" >
				<div class = "is_useful_message" id = "robot_answer_2">Si la réponse n'est pas exacte, veuillez double-cliquer pour signaler
				</div>
				<span class = "clicked" style = "display:none;">Merci</span>
			</div>
		</div>
	</div>"""
    return full_div.format("".join(divs)).replace("\n", "").replace("\xa0", "")

def master_format(output) :
    active = """
            <div class="carousel-item active">
                <div class="card active" style="width: 18rem;">
                <div class="card-body text-center">
                    <h1 class="card-title text-center" style = "font-family: Alegreya Sans ExtraBold, sans-serif;">{program_title}</h1>
                    <p class="card-text text-center" style = "font-family: Alegreya Sans Light, sans-serif;"> <p class = "div_time_ago text-center">Durée :{duration}.</p></p>
                <div class="card-body text-center">
                    <ul class="list-group list-group-flush" style = "font-family: Alegreya Sans Light, sans-serif;">
                        <li class="list-group-item text-center">
                            <p id="goals_{index}" style="display: none">
                                {program_goals}
                            </p>
                            Découvrir les objectifs : <a id="seemoregoals_{index}" onclick="toggleSeeMore('goals_{index}', 'seemoregoals_{index}')" href="javascript:void(0);">Voir plus</a>
                        </li>
                        <li class="list-group-item text-center" style = "font-family: Alegreya Sans Light, sans-serif;">
                            <p id="conditions_{index}" style="display: none">
                                {condition}
                            </p>
                            Découvrir le profil : <a id="seemorecond_{index}" onclick="toggleSeeMore('conditions_{index}', 'seemorecond_{index}')" href="javascript:void(0);">Voir plus</a>
                        </li>
                    </ul>
                </div>
                </div>
                </div>
            </div>"""
    standard = """
            <div class="carousel-item">
                <div class="card" style="width: 18rem;">
                <div class="card-body text-center">
                    <h1 class="card-title text-center" style = "font-family: Alegreya Sans ExtraBold, sans-serif;">{program_title}</h1>
                    <p class="card-text text-center" style = "font-family: Alegreya Sans Light, sans-serif;"> <p class = "div_time_ago text-center">Durée :{duration}.</p></p>
                <div class="card-body text-center">
                    <ul class="list-group list-group-flush" style = "font-family: Alegreya Sans Light, sans-serif;">
                        <li class="list-group-item text-center">
                            <p id="goals_{index}" style="display: none">
                                {program_goals}
                            </p>
                            Découvrir les objectifs : <a id="seemoregoals_{index}" onclick="toggleSeeMore('goals_{index}', 'seemoregoals_{index}')" href="javascript:void(0);">Voir plus</a>
                        </li>
                        <li class="list-group-item text-center" style = "font-family: Alegreya Sans Light, sans-serif;">
                            <p id="conditions_{index}" style="display: none">
                                {condition}
                            </p>
                            Découvrir le profil : <a id="seemorecond_{index}" onclick="toggleSeeMore('conditions_{index}', 'seemorecond_{index}')" href="javascript:void(0);">Voir plus</a>
                        </li>
                    </ul>
                </div>
                </div>
                </div>
            </div>"""
    active_dict = output[0]
    divs = [active.format_map(active_dict)]
    standard_elements = output[1:]
    for element in standard_elements : 
        divs.append(standard.format_map(element))
    full_div = """
	<div class='d-flex flex-row p-3'>
		<div class='w-100'>
			<div class='d-flex justify-content-between align-items-center'>
				<div class='d-flex flex-row align-items-center'>
				</div>
			</div>
                <div id="carouselExampleControls" class="carousel slide" data-ride="carousel">
        <div class="carousel-inner">
            {}
        </div>
        <a class="carousel-control-prev" href="#carouselExampleControls" role="button" data-slide="prev">
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="sr-only">Previous</span>
        </a>
        <a class="carousel-control-next" href="#carouselExampleControls" role="button" data-slide="next">
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="sr-only">Next</span>
        </a>
    </div>
			<div class = "is_useful" >
				<div class = "is_useful_message" id = "robot_answer_2">Si la réponse n'est pas exacte, veuillez double-cliquer pour signaler
				</div>
				<span class = "clicked" style = "display:none;">Merci</span>
			</div>
		</div>
	</div>"""
    return full_div.format("".join(divs)).replace("\n", "").replace("\xa0", "")

def events_format(output) :
    active = """
            <div class="carousel-item active">
                <div class="card active" style="width: 18rem;">
                <div class="card-body text-center">
                    <h1 class="card-title text-center" style = "font-family: Alegreya Sans ExtraBold, sans-serif;">{event_name}</h1>
                    <p class="card-text text-center" style = "font-family: Alegreya Sans Light, sans-serif;">{description} <br /> <p class = "div_time_ago text-center">Prix :{fees}.</p></p>
                <div class="card-body text-center">
                    Date : <strong>{event_date}</strong>
                </div>
                </div>
                </div>
            </div>"""
    standard = """
            <div class="carousel-item">
                <div class="card" style="width: 18rem;">
                <div class="card-body text-center">
                    <h1 class="card-title text-center" style = "font-family: Alegreya Sans ExtraBold, sans-serif;">{event_name}</h1>
                    <p class="card-text text-center" style = "font-family: Alegreya Sans Light, sans-serif;">{description} <br /> <p class = "div_time_ago text-center">Prix :{fees}.</p></p>
                <div class="card-body text-center">
                    Date : <strong>{event_date}</strong>
                </div>
                </div>
                </div>
            </div>"""
    active_dict = output[0]
    divs = [active.format_map(active_dict)]
    standard_elements = output[1:]
    for element in standard_elements : 
        divs.append(standard.format_map(element))
    full_div = """
	<div class='d-flex flex-row p-3'>
		<div class='w-100'>
			<div class='d-flex justify-content-between align-items-center'>
				<div class='d-flex flex-row align-items-center'>
				</div>
			</div>
                <div id="carouselExampleControls" class="carousel slide" data-ride="carousel">
        <div class="carousel-inner">
            {}
        </div>
        <a class="carousel-control-prev" href="#carouselExampleControls" role="button" data-slide="prev">
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="sr-only">Previous</span>
        </a>
        <a class="carousel-control-next" href="#carouselExampleControls" role="button" data-slide="next">
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="sr-only">Next</span>
        </a>
    </div>
			<div class = "is_useful" >
				<div class = "is_useful_message" id = "robot_answer_2">Si la réponse n'est pas exacte, veuillez double-cliquer pour signaler
				</div>
				<span class = "clicked" style = "display:none;">Merci</span>
			</div>
		</div>
	</div>"""
    return full_div.format("".join(divs)).replace("\n", "").replace("\xa0", "")

def news_format(output) :
    active = """
            <div class="carousel-item active">
                <div class="card active" style="width: 18rem;">
                <div class="card-body text-center">
                    <h1 class="card-title text-center" style = "font-family: Alegreya Sans ExtraBold, sans-serif;">{title}</h1>
                    <p class="card-text text-center" style = "font-family: Alegreya Sans Light, sans-serif;">{intro}</p>
                <div class="card-body text-center">
                <a target="_blank" href="{link}" class="btn btn-info" target="_blank">Voir sur le site officiel</a>
                </div>
                </div>
                </div>
            </div>"""
    standard = """
            <div class="carousel-item">
                <div class="card" style="width: 18rem;">
                <div class="card-body text-center">
                    <h1 class="card-title text-center" style = "font-family: Alegreya Sans ExtraBold, sans-serif;">{title}</h1>
                    <p class="card-text text-center" style = "font-family: Alegreya Sans Light, sans-serif;">{intro}</p>
                <div class="card-body text-center">
                <a target="_blank" href="{link}" class="btn btn-info" target="_blank">Voir sur le site officiel</a>
                </div>
                </div>
                </div>
            </div>"""
    active_dict = output[0]
    divs = [active.format_map(active_dict)]
    standard_elements = output[1:]
    for element in standard_elements : 
        divs.append(standard.format_map(element))
    full_div = """
	<div class='d-flex flex-row p-3'>
		<div class='w-100'>
			<div class='d-flex justify-content-between align-items-center'>
				<div class='d-flex flex-row align-items-center'>
				</div>
			</div>
                <div id="carouselExampleControls" class="carousel slide" data-ride="carousel">
        <div class="carousel-inner">
            {}
        </div>
        <a class="carousel-control-prev" href="#carouselExampleControls" role="button" data-slide="prev">
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="sr-only">Previous</span>
        </a>
        <a class="carousel-control-next" href="#carouselExampleControls" role="button" data-slide="next">
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="sr-only">Next</span>
        </a>
    </div>
			<div class = "is_useful" >
				<div class = "is_useful_message" id = "robot_answer_2">Si la réponse n'est pas exacte, veuillez double-cliquer pour signaler
				</div>
				<span class = "clicked" style = "display:none;">Merci</span>
			</div>
		</div>
	</div>"""
    return full_div.format("".join(divs)).replace("\n", "").replace("\xa0", "")

def eng_fields_fone(output) :
    card = """
    <div class='d-flex flex-row p-3'>
		<div class='w-100'>
			<div class='d-flex justify-content-between align-items-center'>
				<div class='d-flex flex-row align-items-center'>
				</div>
			</div>
 			<div class="card active" style="width: 18rem;">
                <div class="card-body text-center">
                    <h1 class="card-title text-center" style = "font-family: Alegreya Sans ExtraBold, sans-serif;">{program_title}</h1>
                    <p class="card-text text-center" style = "font-family: Alegreya Sans Light, sans-serif;">{fields} <br /> <p class = "div_time_ago text-center">Durée de la formation :{duration}.</p></p>
                    <ul class="list-group list-group-flush" style = "font-family: Alegreya Sans Light, sans-serif;">
                        <li class="list-group-item text-center">
                            <p id="goals_{index}" style="display: none">
                                {program_goals}
                            </p>
                            Découvrir les objectifs : <a id="seemoregoals_{index}" onclick="toggleSeeMore('goals_{index}', 'seemoregoals_{index}')" href="javascript:void(0);">Voir plus</a>
                        </li>
                        <li class="list-group-item text-center" style = "font-family: Alegreya Sans Light, sans-serif;">
                            <p id="conditions_{index}" style="display: none">
                                {profil}
                            </p>
                            Découvrir le profil : <a id="seemorecond_{index}" onclick="toggleSeeMore('conditions_{index}', 'seemorecond_{index}')" href="javascript:void(0);">Voir plus</a>
                        </li>
                    </ul>
                <div class="card-body text-center">
                <a target="_blank" href="{descriptif}" class="btn btn-info">Récupérer le descriptif complet</a>
                </div>
                </div>
            </div>

			<div class = "is_useful" >
				<div class = "is_useful_message" id = "robot_answer_2">Si la réponse n'est pas exacte, veuillez double-cliquer pour signaler
				</div>
				<span class = "clicked" style = "display:none;">Merci</span>
			</div>
		</div>
	</div>"""
    return card.format_map(output).replace("\n", "")

def eng_fields_format(output) :
    active = """
            <div class="carousel-item active">
                <div class="card active" style="width: 18rem;">
                <div class="card-body text-center">
                    <h1 class="card-title text-center" style = "font-family: Alegreya Sans ExtraBold, sans-serif;">{program_title}</h1>
                    <p class="card-text text-center" style = "font-family: Alegreya Sans Light, sans-serif;">{fields} <br /> <p class = "div_time_ago text-center">Durée de la formation :{duration}.</p></p>
                    <ul class="list-group list-group-flush" style = "font-family: Alegreya Sans Light, sans-serif;">
                        <li class="list-group-item text-center">
                            <p id="goals_{index}" style="display: none">
                                {program_goals}
                            </p>
                            Découvrir les objectifs : <a id="seemoregoals_{index}" onclick="toggleSeeMore('goals_{index}', 'seemoregoals_{index}')" href="javascript:void(0);">Voir plus</a>
                        </li>
                        <li class="list-group-item text-center" style = "font-family: Alegreya Sans Light, sans-serif;">
                            <p id="conditions_{index}" style="display: none">
                                {profil}
                            </p>
                            Découvrir le profil : <a id="seemorecond_{index}" onclick="toggleSeeMore('conditions_{index}', 'seemorecond_{index}')" href="javascript:void(0);">Voir plus</a>
                        </li>
                    </ul>
                <div class="card-body text-center">
                <a target="_blank" href="{descriptif}" class="btn btn-info">Récupérer le descriptif complet</a>
                </div>
                </div>
                </div>
            </div>"""
    standard = """
            <div class="carousel-item">
                <div class="card" style="width: 18rem;">
                <div class="card-body text-center">
                    <h1 class="card-title text-center" style = "font-family: Alegreya Sans ExtraBold, sans-serif;">{program_title}</h1>
                    <p class="card-text text-center" style = "font-family: Alegreya Sans Light, sans-serif;">{fields} <br /> <p class = "div_time_ago text-center">Durée de la formation :{duration}.</p></p>
                    <ul class="list-group list-group-flush" style = "font-family: Alegreya Sans Light, sans-serif;">
                        <li class="list-group-item text-center">
                            <p id="goals_{index}" style="display: none">
                                {program_goals}
                            </p>
                            Découvrir les objectifs : <a id="seemoregoals_{index}" onclick="toggleSeeMore('goals_{index}', 'seemoregoals_{index}')" href="javascript:void(0);">Voir plus</a>
                        </li>
                        <li class="list-group-item text-center">
                            <p id="conditions_{index}" style="display: none">
                                {profil}
                            </p>
                            Découvrir le profil : <a id="seemorecond_{index}" onclick="toggleSeeMore('conditions_{index}', 'seemorecond_{index}')" href="javascript:void(0);">Voir plus</a>
                        </li>
                    </ul>
                <div class="card-body text-center">
                <a target="_blank" href="{descriptif}" class="btn btn-info">Récupérer le descriptif complet</a>
                </div>
                </div>
                </div>
            </div>"""
    active_dict = output[0]
    divs = [active.format_map(active_dict)]
    standard_elements = output[1:]
    for element in standard_elements : 
        divs.append(standard.format_map(element))
    full_div = """
	<div class='d-flex flex-row p-3'>
		<div class='w-100'>
			<div class='d-flex justify-content-between align-items-center'>
				<div class='d-flex flex-row align-items-center'>
				</div>
			</div>
                <div id="carouselExampleControls" class="carousel slide" data-ride="carousel">
        <div class="carousel-inner">
            {}
        </div>
        <a class="carousel-control-prev" href="#carouselExampleControls" role="button" data-slide="prev">
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="sr-only">Previous</span>
        </a>
        <a class="carousel-control-next" href="#carouselExampleControls" role="button" data-slide="next">
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="sr-only">Next</span>
        </a>
    </div>
			<div class = "is_useful" >
				<div class = "is_useful_message" id = "robot_answer_2">Si la réponse n'est pas exacte, veuillez double-cliquer pour signaler
				</div>
				<span class = "clicked" style = "display:none;">Merci</span>
			</div>
		</div>
	</div>"""
    return full_div.format("".join(divs)).replace("\n", "")

def connect_db(hote, usr, pwd, db) :
    conn_main = mysql.connector.connect(
        host = hote,
        user = usr,
        password = pwd,
        database = db
    )  
    if (conn_main) : 
        print("connected succesfully !")
        return conn_main
    else : 
        print("Failed !")
        return -1

def select_from_where_one(connection, table_name, key, value) : 
    sql_req = 'SELECT * FROM {} WHERE {} = "{}"'.format(
        table_name, 
        key, 
        value)
    cursor = connection.cursor()
    cursor.execute(sql_req)
    records = cursor.fetchone()
    
    if records: 
        columnNames = [column[0] for column in cursor.description]
        rows_dict = dict(zip(columnNames , records))
        return rows_dict
    else : 
        print("Désolé je peux trouver un laboratoire veuillez choisir un autre titre !")
        return None

def select_from_where(connection, table_name, key, value) : 
    sql_req = 'SELECT * FROM {} WHERE {} = "{}"'.format(
        table_name, 
        key, 
        value)
    cursor = connection.cursor()
    cursor.execute(sql_req)
    records = cursor.fetchall()
    
    if records: 
        ret_array = []
        for record in records : 
            columnNames = [column[0] for column in cursor.description]
            rows_dict = dict(zip(columnNames , record))
            ret_array.append(rows_dict)
        return ret_array
    else : 
        print("Désolé je peux trouver un laboratoire veuillez choisir un autre titre !")
        return None
    

def select_from_all(connection, table_name) : 
    sql_req = 'SELECT * FROM {}'.format(table_name)
    
    cursor = connection.cursor()
    cursor.execute(sql_req)
    records = cursor.fetchall()
    
    if records : 
        insertObject = []
        columnNames = [column[0] for column in cursor.description]
        for record in records:
            insertObject.append( dict( zip( columnNames , record ) ) )
        return insertObject
    else : 
        print("Désolé je peux trouver un laboratoire veuillez choisir un autre titre !")
        return None



def format_labs_output(output) :
    """
    This function takes in argument the output in format of list of tuples 
    And returns a well formated string that fits RASA requirements
    """
    img_data_labs = {
                 "si2m" : "PD94bWwgdmVyc2lvbj0iMS4wIiBzdGFuZGFsb25lPSJubyI/Pgo8IURPQ1RZUEUgc3ZnIFBVQkxJQyAiLS8vVzNDLy9EVEQgU1ZHIDIwMDEwOTA0Ly9FTiIKICJodHRwOi8vd3d3LnczLm9yZy9UUi8yMDAxL1JFQy1TVkctMjAwMTA5MDQvRFREL3N2ZzEwLmR0ZCI+CjxzdmcgdmVyc2lvbj0iMS4wIiB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciCiB3aWR0aD0iMzE2LjAwMDAwMHB0IiBoZWlnaHQ9IjIyNy4wMDAwMDBwdCIgdmlld0JveD0iMCAwIDMxNi4wMDAwMDAgMjI3LjAwMDAwMCIKIHByZXNlcnZlQXNwZWN0UmF0aW89InhNaWRZTWlkIG1lZXQiPgo8bWV0YWRhdGE+CkNyZWF0ZWQgYnkgcG90cmFjZSAxLjE2LCB3cml0dGVuIGJ5IFBldGVyIFNlbGluZ2VyIDIwMDEtMjAxOQo8L21ldGFkYXRhPgo8ZyB0cmFuc2Zvcm09InRyYW5zbGF0ZSgwLjAwMDAwMCwyMjcuMDAwMDAwKSBzY2FsZSgwLjEwMDAwMCwtMC4xMDAwMDApIgpmaWxsPSIjMDAwMDAwIiBzdHJva2U9Im5vbmUiPgo8cGF0aCBkPSJNNzIwIDE2NDQgYy0xNDMgLTEwIC0zODkgLTU3IC01MjAgLTEwMSAtNzQgLTI1IC0xNDEgLTUwIC0xNDcgLTU1Ci0yMSAtMTcgLTE2IC0xMjIgNyAtMTcyIDE3IC0zNSAyOCAtNDUgNTkgLTU1IDI3IC04IDQ3IC04IDY1IC0xIDE0IDUgMzIgNyAzOQo0IDggLTMgNDkgNyA5MyAyMSAxNTUgNTEgMjUyIDY1IDQ1NyA2NiAxMjMgMSAxNzEgLTQgMjUyIC0yMiA1NSAtMTIgMTExIC0yMQoxMjUgLTIxIDE0IDAgNTcgLTEwIDk1IC0yMyAzOSAtMTMgODYgLTI4IDEwNSAtMzMgMTkgLTYgNDMgLTEzIDU0IC0xNyAxNiAtNwoxNyAtNCAxMiAyMSAtNiAyNiAtMyAzMSAyNCA0MSAzMyAxMiA1MCA0NiA1MCA5OCAwIDM0IC01IDQxIC00NSA3MCAtMTcgMTMKLTE4IDE2IC01IDI0IDIwIDE0IDcgMjQgLTY1IDQ5IC0yMjEgNzggLTQ2NyAxMTggLTY1NSAxMDZ6Ii8+CjxwYXRoIGQ9Ik0xMjQ3IDExMzAgYy02NSAtMTEgLTE4MyAtNDggLTIyOCAtNzAgLTU2IC0yOSAtNjEgLTQwIC00NCAtOTYgOAotMjcgMTUgLTc0IDE1IC0xMDUgMCAtMzEgNiAtNjMgMTQgLTc0IDEzIC0xOCAxNSAtMTggNjIgMTMgODcgNTUgMTQzIDc1IDIxNgo3NiA1MiAxIDcyIC0zIDk0IC0yMCA3NCAtNTUgOTAgLTExNyA0OSAtMTk5IC00MyAtOTAgLTIwNiAtMjgzIC0yNzUgLTMyOCAtMTQKLTkgLTU0IC0yMCAtODggLTI2IC0zNSAtNiAtNjkgLTE1IC03NiAtMjAgLTEwIC04IC04IC0zMyA5IC0xMTMgbDIxIC0xMDMgNzAKMSBjMzggMCAxNTkgNCAyNjkgOCAxNDIgNiAyMjYgNSAyOTAgLTQgNTAgLTYgMTExIC0xNCAxMzYgLTE3IGw0NiAtNSA2IDE0MgpjNCA3OCA0IDE0NyAwIDE1MyAtNCA3IC02NyA4IC0xODcgNCBsLTE4MSAtNiA1NiA1MiBjMTIyIDExMiAyMDcgMjMzIDI0MCAzMzgKMjMgNzMgMjQgMTE5IDQgMTg2IC00OSAxNjQgLTI3MCAyNTQgLTUxOCAyMTN6Ii8+CjxwYXRoIGQ9Ik0zNjcgOTQ1IGMtMTY5IC00NyAtMjYxIC0xNTIgLTI0NCAtMjgwIDkgLTU5IDI5IC05OCA4NyAtMTY1IDU5IC03MAo3MCAtOTAgNzAgLTEzNSAwIC01MCAtNDEgLTg3IC0xMTkgLTEwOSAtNDQgLTEyIC02MSAtMjIgLTYxIC0zNCAwIC05IDE5IC01MQo0MyAtOTIgbDQyIC03NSA0NiAxIGM5MyAxIDIzMyA5NCAyODAgMTg1IDUwIDk5IDMzIDE5MiAtNTcgMzA0IC02NSA4MSAtODQKMTE1IC04NCAxNDcgMCA0NiA0NiA3OCAxMTIgNzggMjcgMCA0OCA0IDQ4IDkgMCA0IC0xOCA0NyAtNDAgOTUgLTQ1IDk0IC00Mwo5MyAtMTIzIDcxeiIvPgo8cGF0aCBkPSJNNjM4IDUwOCBjLTUgLTM3MyAtMyAtNDI0IDEwIC00MzUgMTkgLTE1IDE5OSAtMTggMjIxIC00IDEzIDggMTUgNzcKMTYgNDM1IGwxIDQyNiAtMTIyIDAgLTEyMiAwIC00IC00MjJ6Ii8+CjxwYXRoIGQ9Ik0xOTE4IDkyMyBjLTMgLTQgLTEgLTEwMCAzIC0yMTMgNCAtMTE3IDMgLTI5NSAtMiAtNDE0IC02IC0xMjQgLTcKLTIxMiAtMSAtMjE4IDUgLTUgNTggLTcgMTE4IC02IGwxMDkgMyA1IDE5OCA1IDE5OCA0NCAtMTAzIGMyNSAtNTcgNjYgLTE0OQo5MyAtMjA2IDQ1IC05OCA0OSAtMTAzIDc1IC0xMDAgMzMgNCAzMiAxIDEyNSAyMzMgMzggOTQgNzQgMTc1IDgwIDE4MCA3IDcgOQotNTMgNyAtMTk1IGwtNCAtMjA1IDEyMCAwIDEyMCAwIDEgNDI4IDEgNDI3IC0xMTIgMCAtMTExIDAgLTEwOSAtMjI1IGMtNTkKLTEyNCAtMTEyIC0yMjUgLTExNiAtMjI1IC0xMiAwIC0xNyAxMCAtMTIxIDIzNSBsLTk3IDIxMCAtMTE0IDMgYy02NCAxIC0xMTcKLTEgLTExOSAtNXoiLz4KPC9nPgo8L3N2Zz4K", 
                 "masafeq" : "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",
                 "ges3d" : "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"
                    }
    lab_key = output["acronyme"]
    output["img_data"] = img_data_labs[lab_key]
    output["acronyme"] = lab_key.upper()
    
    string_labs = """
    <div class='d-flex flex-row p-3'>
        <div class='w-100'>
            <div class='d-flex justify-content-between align-items-center'>
                <div class='d-flex flex-row align-items-center'>
                </div>
            </div>
            <div class='card' style='width: 18rem;'>
                <div class = 'text-center'><img class='card-img-top ' src='data:image/svg+xml;base64,{img_data}' alt='Card image cap' style = 'max-height: 200px;max-width: 200px;'></div>
                    <div class='card-body'>
                        <h1 class='card-title text-center' style = "font-family: 'Alegreya Sans ExtraBold', sans-serif;">{acronyme}</h1>
                        <p class='card-text text-center' style = "font-family: 'Alegreya Sans Light', sans-serif;">{intitulé}</p>
                    </div>
                    <ul class='list-group list-group-flush'>
                    <li class='list-group-item bot_corps text-center'>Responsable : <a href = 'mailto: {email_reponsable}'>{Responsable}</a></li>
                    <li class='list-group-item text-center' style = "font-family: 'Alegreya Sans Light', sans-serif;">disciplines : {disciplines}</li>
                    </ul>
                <div class='card-body text-center'>
                <a target="_blank" href='{descriptif}' class="btn btn-info">Récupérer la description complète</a>
                </div>
            </div>
            <div class = "is_useful" >
                <div class = "is_useful_message" id = "robot_answer_2">Si la réponse n'est pas exacte, veuillez double-cliquer pour signaler
                </div>
                <span class = "clicked" style = "display:none;">Merci</span>
            </div>
        </div>
    </div>""".format_map(output)
    
    return string_labs.replace("\n", "")


def format_faculty(output) : 
    active = """
            <div class="carousel-item active">
                <div class="card active" style="width: 18rem;">
                <img class="card-img-top" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNTYgMjU2Ij48cmVjdCB3aWR0aD0iMjU2IiBoZWlnaHQ9IjI1NiIgZmlsbD0ibm9uZSIvPjxjaXJjbGUgY3g9IjEwNCIgY3k9IjE0NCIgcj0iMzIiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2Utd2lkdGg9IjgiLz48cGF0aCBmaWxsPSJub25lIiBzdHJva2U9IiMwMDAiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLXdpZHRoPSI4IiBkPSJNNTMuMzg5NjQsMjA3Ljk5ODc2YTU2LjAyMjk0LDU2LjAyMjk0LDAsMCwxLDEwMS4yMjA3MiwwTDIxNS45OTk4NCwyMDhBOCw4LDAsMCwwLDIyNCwyMDBWNTZhOCw4LDAsMCwwLTgtOEg0MGE4LDgsMCwwLDAtOCw4VjIwMC4wMDA3NEE3Ljk5OTI2LDcuOTk5MjYsMCwwLDAsNDAsMjA4WiIvPjxwb2x5bGluZSBmaWxsPSJub25lIiBzdHJva2U9IiMwMDAiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLXdpZHRoPSI4IiBwb2ludHM9IjE3NiAxNzYgMTkyIDE3NiAxOTIgODAgNjQgODAgNjQgOTYiLz48L3N2Zz4=" alt="Card image cap">
                <div class="card-body text-center">
                    <h1 class="card-title text-center" style = "font-family: Alegreya Sans ExtraBold, sans-serif;">{Nom} {Prénom}</h1>
                    <p class="card-text text-center" style = "font-family: Alegreya Sans Light, sans-serif;">Professeur permanant à INSEA en {Departement}</p>
                <ul class="list-group list-group-flush">
                    <li class="list-group-item bot_corps text-center">Email : {E-mail}</a></li>
                    <li class="list-group-item text-center" style = "font-family: Alegreya Sans Light, sans-serif;">Bureau : {Bureau}</li>
                </ul>
                </div>
                </div>
            </div>"""
    standard = """
            <div class="carousel-item">
                <div class="card" style="width: 18rem;">
                <img class="card-img-top" src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNTYgMjU2Ij48cmVjdCB3aWR0aD0iMjU2IiBoZWlnaHQ9IjI1NiIgZmlsbD0ibm9uZSIvPjxjaXJjbGUgY3g9IjEwNCIgY3k9IjE0NCIgcj0iMzIiIGZpbGw9Im5vbmUiIHN0cm9rZT0iIzAwMCIgc3Ryb2tlLWxpbmVjYXA9InJvdW5kIiBzdHJva2UtbGluZWpvaW49InJvdW5kIiBzdHJva2Utd2lkdGg9IjgiLz48cGF0aCBmaWxsPSJub25lIiBzdHJva2U9IiMwMDAiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLXdpZHRoPSI4IiBkPSJNNTMuMzg5NjQsMjA3Ljk5ODc2YTU2LjAyMjk0LDU2LjAyMjk0LDAsMCwxLDEwMS4yMjA3MiwwTDIxNS45OTk4NCwyMDhBOCw4LDAsMCwwLDIyNCwyMDBWNTZhOCw4LDAsMCwwLTgtOEg0MGE4LDgsMCwwLDAtOCw4VjIwMC4wMDA3NEE3Ljk5OTI2LDcuOTk5MjYsMCwwLDAsNDAsMjA4WiIvPjxwb2x5bGluZSBmaWxsPSJub25lIiBzdHJva2U9IiMwMDAiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCIgc3Ryb2tlLXdpZHRoPSI4IiBwb2ludHM9IjE3NiAxNzYgMTkyIDE3NiAxOTIgODAgNjQgODAgNjQgOTYiLz48L3N2Zz4=" alt="Card image cap">
                <div class="card-body text-center">
                    <h1 class="card-title text-center" style = "font-family: Alegreya Sans ExtraBold, sans-serif;">{Nom} {Prénom}</h1>
                    <p class="card-text text-center" style = "font-family: Alegreya Sans Light, sans-serif;">Professeur permanant à INSEA en {Departement}.</p>
                <ul class="list-group list-group-flush">
                    <li class="list-group-item bot_corps text-center">Email : {E-mail}</a></li>
                    <li class="list-group-item text-center" style = "font-family: Alegreya Sans Light, sans-serif;">Bureau : {Bureau}</li>
                </ul>
                </div>
                </div>
            </div>"""
    active_dict = output[0]
    divs = [active.format_map(active_dict)]
    standard_elements = output[1:]
    for element in standard_elements : 
        divs.append(standard.format_map(element))
    full_div = """
	<div class='d-flex flex-row p-3'>
		<div class='w-100'>
			<div class='d-flex justify-content-between align-items-center'>
				<div class='d-flex flex-row align-items-center'>
				</div>
			</div>
                <div id="carouselExampleControls" class="carousel slide" data-ride="carousel">
        <div class="carousel-inner">
            {}
        </div>
        <a class="carousel-control-prev" href="#carouselExampleControls" role="button" data-slide="prev">
            <span class="carousel-control-prev-icon" aria-hidden="true"></span>
            <span class="sr-only">Previous</span>
        </a>
        <a class="carousel-control-next" href="#carouselExampleControls" role="button" data-slide="next">
            <span class="carousel-control-next-icon" aria-hidden="true"></span>
            <span class="sr-only">Next</span>
        </a>
    </div>
			<div class = "is_useful" >
				<div class = "is_useful_message" id = "robot_answer_2">Si la réponse n'est pas exacte, veuillez double-cliquer pour signaler
				</div>
				<span class = "clicked" style = "display:none;">Merci</span>
			</div>
		</div>
	</div>"""
    return full_div.format("".join(divs)).replace("\n", "")
    


