class BaseTaxAdapter:
    """ Базовый интерфейс для всех налоговых адаптеров """
    def send_report(self, data):
        raise NotImplementedError
    
    def get_status(self, report_id):
        raise NotImplementedError
        
    def validate(self, data):
        raise NotImplementedError


class RestTaxAdapter(BaseTaxAdapter):
    """ Адаптер для REST/JSON """
    def send_report(self, data):
        return {"protocol": "REST", "info": "Data sent as JSON"}

    def get_status(self, report_id):
        return {"report_id": report_id, "status": "in_progress", "provider": "REST_Service"}

    def validate(self, data):
        return {"is_valid": True, "protocol": "REST", "message": "JSON schema is valid"}


class SoapTaxAdapter(BaseTaxAdapter):
    """ Адаптер для SOAP/XML """
    def send_report(self, data):
        #Здесь будет вызываться сериализатор и конвертер из JSON в XML.
        return {"protocol": "SOAP", "info": "Data wrapped in XML Envelope"}

    def get_status(self, report_id):
        return {"report_id": report_id, "status": "pending", "provider": "SOAP_Service"}

    def validate(self, data):
        return {"is_valid": True, "protocol": "SOAP", "message": "XML structure is correct"}


def get_adapter(country):
    """ Фабрика: выбирает адаптер на основе страны """
    mapping = {
        'russia': RestTaxAdapter(),
        'other': SoapTaxAdapter()
    }
    # Если страна неизвестна, отдаем REST как стандарт
    return mapping.get(country, RestTaxAdapter())