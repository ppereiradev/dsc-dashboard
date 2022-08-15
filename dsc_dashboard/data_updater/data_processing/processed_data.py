from .diretoria import Diretoria
from .conectividade import Conectividade
from .sistemas import Sistemas
from .servicos_computacionais import ServicosComputacionais
from .micro_informatica import MicroInformatica
from .suporte import Suporte

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
        
class ProcessedData(metaclass=Singleton):
    def __init__(self):
        self.diretoria = Diretoria()
        self.conectividade = Conectividade()
        self.sistemas = Sistemas()
        self.servicos_computacionais = ServicosComputacionais()
        self.micro_informatica = MicroInformatica()
        self.suporte = Suporte()
        self.get_processed_data_all()

    def get_processed_data_all(self):
        self.diretoria.get_processed_data()
        self.conectividade.get_processed_data()
        self.sistemas.get_processed_data()
        self.servicos_computacionais.get_processed_data()
        self.micro_informatica.get_processed_data()
        self.suporte.get_processed_data()

    def get_data_diretoria(self):
        return self.diretoria

    def get_data_conectividade(self):
        return self.conectividade
    
    def get_data_sistemas(self, group=None):
        if group:
            self.sistemas.get_processed_data(group)
        else:
            self.sistemas.get_processed_data()
        return self.sistemas

    def get_data_servicos_computacionais(self):
        return self.servicos_computacionais

    def get_data_micro_informatica(self):
        return self.micro_informatica

    def get_data_suporte(self):
        return self.suporte
