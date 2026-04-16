"""
automacao_boas_praticas.py

Automação Python seguindo as boas práticas do Lab 1.1 - BotCity.
Referência: https://treinamentorpa.botcity.dev/labs/automacoes/boas-praticas/

Boas práticas aplicadas:
    1.  PEP 8  - Estilo de Código
    2.  PEP 257 - Docstrings
    3.  PEP 484/585 - Type Hints
    4.  PEP 586 - TypedDict
    5.  PEP 3134 - Tratamento de Exceções
    6.  PEP 391 - Logging Configurado
    7.  Modularização - Separar por Responsabilidade
    8.  Validação de Entrada
    9.  Configuração Centralizada
    10. Testes Unitários
"""

# =============================================================================
# IMPORTS
# =============================================================================
import csv
import logging
import logging.config
import logging.handlers
import os
import unittest
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional
from typing import TypedDict


# =============================================================================
# BOA PRÁTICA 9 - Configuração Centralizada (deve ser carregada primeiro)
# =============================================================================
class Config:
    """
    Configurações centralizadas da automação.

    Lê variáveis de ambiente com fallback para valores padrão.
    Nunca use credenciais hardcoded no código!
    """

    BASE_DIR: Path = Path(__file__).parent

    # Banco de dados
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_USER: str = os.getenv("DB_USER", "user")
    DB_PASS: str = os.getenv("DB_PASS", "password")
    DB_NAME: str = os.getenv("DB_NAME", "database")

    # API
    API_URL: str = os.getenv("API_URL", "https://api.example.com")
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "30"))
    API_RETRIES: int = int(os.getenv("API_RETRIES", "3"))

    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: Path = BASE_DIR / "logs"


# =============================================================================
# BOA PRÁTICA 6 - Logging Configurado (PEP 391)
# =============================================================================
def configurar_logging() -> None:
    """
    Configura o sistema de logging da automação.

    Utiliza logging estruturado com saída para console e arquivo rotativo.
    Evite usar print() — prefira sempre o logger.
    """
    Config.LOG_DIR.mkdir(exist_ok=True)

    config_logging = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "padrao": {
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": "INFO",
                "formatter": "padrao",
            },
            "arquivo": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": str(Config.LOG_DIR / "automacao.log"),
                "maxBytes": 10 * 1024 * 1024,  # 10 MB
                "backupCount": 5,
                "level": "DEBUG",
                "formatter": "padrao",
            },
        },
        "root": {
            "level": Config.LOG_LEVEL,
            "handlers": ["console", "arquivo"],
        },
    }

    logging.config.dictConfig(config_logging)


configurar_logging()
logger = logging.getLogger(__name__)


# =============================================================================
# BOA PRÁTICA 4 - TypedDict (PEP 586)
# =============================================================================
class UsuarioDict(TypedDict):
    """Estrutura tipada para representar um usuário."""

    id: int
    nome: str
    email: str
    ativo: bool


class ResultadoProcessamento(TypedDict):
    """Resultado do processamento de um usuário."""

    usuario_id: int
    status: str
    mensagem: str


# =============================================================================
# BOA PRÁTICA 8 - Validação de Entrada
# =============================================================================
@dataclass
class ConfiguracaoAutomacao:
    """
    Configuração da automação com validação automática.

    Args:
        url: URL base da API (deve começar com http:// ou https://)
        timeout: Tempo máximo de espera em segundos (deve ser > 0)
        retries: Número de tentativas em caso de falha (deve ser >= 0)
    """

    url: str
    timeout: int = 30
    retries: int = 3

    def __post_init__(self) -> None:
        """Valida os parâmetros após a inicialização."""
        if not self.url.startswith(("http://", "https://")):
            raise ValueError(f"URL inválida: '{self.url}'. Deve começar com http:// ou https://")
        if self.timeout <= 0:
            raise ValueError(f"Timeout deve ser positivo. Recebido: {self.timeout}")
        if self.retries < 0:
            raise ValueError(f"Retries não pode ser negativo. Recebido: {self.retries}")


# =============================================================================
# BOA PRÁTICA 7 - Modularização / BOA PRÁTICA 2 - Docstrings (PEP 257)
# BOA PRÁTICA 3 - Type Hints (PEP 484/585)
# =============================================================================
class ProcessadorCSV:
    """
    Processa arquivos CSV com leitura e escrita seguras.

    Segue o princípio de responsabilidade única (SRP):
    esta classe só lida com operações de CSV.
    """

    def __init__(self, encoding: str = "utf-8") -> None:
        """
        Inicializa o processador CSV.

        Args:
            encoding: Codificação do arquivo (padrão: utf-8).
        """
        self.encoding = encoding

    def ler(self, arquivo: str) -> list[dict]:
        """
        Lê um arquivo CSV e retorna lista de dicionários.

        Args:
            arquivo: Caminho para o arquivo CSV.

        Returns:
            Lista de dicionários representando as linhas do CSV.

        Raises:
            FileNotFoundError: Se o arquivo não existir.
            RuntimeError: Em caso de erro na leitura.
        """
        caminho = Path(arquivo)

        if not caminho.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {arquivo}")

        try:
            with open(caminho, "r", encoding=self.encoding) as f:
                leitor = csv.DictReader(f)
                dados = list(leitor)
            logger.info(f"CSV lido com sucesso: {arquivo} ({len(dados)} registros)")
            return dados
        except Exception as e:
            logger.error(f"Erro ao ler CSV '{arquivo}': {e}", exc_info=True)
            raise RuntimeError("Falha na leitura do CSV") from e

    def escrever(self, arquivo: str, dados: list[dict]) -> None:
        """
        Escreve dados em um arquivo CSV.

        Args:
            arquivo: Caminho de destino para o CSV.
            dados: Lista de dicionários a serem escritos.

        Raises:
            ValueError: Se a lista de dados estiver vazia.
            RuntimeError: Em caso de erro na escrita.
        """
        if not dados:
            raise ValueError("Não é possível escrever um CSV com dados vazios.")

        try:
            campos = dados[0].keys()
            with open(arquivo, "w", newline="", encoding=self.encoding) as f:
                escritor = csv.DictWriter(f, fieldnames=campos)
                escritor.writeheader()
                escritor.writerows(dados)
            logger.info(f"CSV escrito com sucesso: {arquivo} ({len(dados)} registros)")
        except Exception as e:
            logger.error(f"Erro ao escrever CSV '{arquivo}': {e}", exc_info=True)
            raise RuntimeError("Falha na escrita do CSV") from e


class ProcessadorDados:
    """
    Processa e valida dados de usuários.

    Responsabilidade: orquestrar as regras de negócio da automação.
    """

    def __init__(self, callback: Optional[Callable[[str], None]] = None) -> None:
        """
        Inicializa o processador.

        Args:
            callback: Função opcional chamada após cada processamento.
        """
        self.callback = callback

    def processar_usuario(self, usuario: UsuarioDict) -> ResultadoProcessamento:
        """
        Processa um único usuário tipado.

        Args:
            usuario: Dicionário tipado com dados do usuário.

        Returns:
            ResultadoProcessamento com status e mensagem.
        """
        logger.debug(f"Processando usuário ID={usuario['id']}: {usuario['nome']}")

        if not usuario.get("ativo"):
            resultado: ResultadoProcessamento = {
                "usuario_id": usuario["id"],
                "status": "ignorado",
                "mensagem": f"Usuário '{usuario['nome']}' está inativo.",
            }
            logger.warning(resultado["mensagem"])
        else:
            resultado = {
                "usuario_id": usuario["id"],
                "status": "sucesso",
                "mensagem": f"Usuário '{usuario['nome']}' processado com sucesso.",
            }
            logger.info(resultado["mensagem"])

        if self.callback:
            self.callback(resultado["mensagem"])

        return resultado

    def processar_lista(self, usuarios: list[UsuarioDict]) -> list[ResultadoProcessamento]:
        """
        Processa uma lista de usuários.

        Args:
            usuarios: Lista de usuários tipados.

        Returns:
            Lista de resultados de processamento.
        """
        resultados = []
        for usuario in usuarios:
            try:
                resultado = self.processar_usuario(usuario)
                resultados.append(resultado)
            except Exception as e:
                # BOA PRÁTICA 5 - Tratamento de Exceções com contexto (PEP 3134)
                logger.error(
                    f"Erro ao processar usuário ID={usuario.get('id')}: {e}",
                    exc_info=True,
                )
                raise RuntimeError(
                    f"Falha no processamento do usuário {usuario.get('id')}"
                ) from e

        logger.info(f"Processamento concluído: {len(resultados)} usuários.")
        return resultados


# =============================================================================
# BOA PRÁTICA 1 - PEP 8: nomes, constantes e formatação
# =============================================================================
MAX_USUARIOS_POR_LOTE: int = 100  # Constante: UPPER_SNAKE_CASE


def buscar_usuarios_por_ids(ids: list[int]) -> dict[int, str]:
    """
    Simula busca de usuários por lista de IDs.

    Args:
        ids: Lista de IDs de usuários.

    Returns:
        Dicionário mapeando ID -> nome do usuário.
    """
    # Simulação — em produção, consultaria um banco ou API
    banco_simulado = {
        1: "Ana Paula",
        2: "Carlos Eduardo",
        3: "Mariana Lima",
    }
    return {uid: banco_simulado[uid] for uid in ids if uid in banco_simulado}


def enviar_notificacao(destinatario: str, assunto: Optional[str] = None) -> bool:
    """
    Simula envio de notificação.

    Args:
        destinatario: E-mail ou identificador do destinatário.
        assunto: Assunto opcional da notificação.

    Returns:
        True se o envio foi bem-sucedido, False caso contrário.
    """
    assunto_final = assunto or "(sem assunto)"
    logger.info(f"Notificação enviada para '{destinatario}' | Assunto: '{assunto_final}'")
    return True


# =============================================================================
# BOA PRÁTICA 10 - Testes Unitários
# =============================================================================
class TestProcessadorCSV(unittest.TestCase):
    """Testes unitários para a classe ProcessadorCSV."""

    def setUp(self) -> None:
        """Cria arquivo CSV temporário para os testes."""
        self.processador = ProcessadorCSV()
        self.arquivo_temp = Path("temp_teste.csv")
        self.arquivo_temp.write_text("nome,idade\nJoão,30\nMaria,25\n", encoding="utf-8")

    def tearDown(self) -> None:
        """Remove arquivos temporários após cada teste."""
        if self.arquivo_temp.exists():
            self.arquivo_temp.unlink()
        saida = Path("saida_teste.csv")
        if saida.exists():
            saida.unlink()

    def test_ler_csv_valido(self) -> None:
        """Deve ler CSV e retornar lista de dicionários corretamente."""
        dados = self.processador.ler(str(self.arquivo_temp))
        self.assertEqual(len(dados), 2)
        self.assertEqual(dados[0]["nome"], "João")
        self.assertEqual(dados[1]["nome"], "Maria")

    def test_ler_csv_inexistente(self) -> None:
        """Deve lançar FileNotFoundError para arquivo inexistente."""
        with self.assertRaises(FileNotFoundError):
            self.processador.ler("arquivo_que_nao_existe.csv")

    def test_escrever_csv(self) -> None:
        """Deve escrever CSV e verificar conteúdo."""
        dados = [{"nome": "Pedro", "cidade": "São Paulo"}]
        self.processador.escrever("saida_teste.csv", dados)
        conteudo = Path("saida_teste.csv").read_text(encoding="utf-8")
        self.assertIn("Pedro", conteudo)
        self.assertIn("São Paulo", conteudo)

    def test_escrever_csv_dados_vazios(self) -> None:
        """Deve lançar ValueError ao tentar escrever dados vazios."""
        with self.assertRaises(ValueError):
            self.processador.escrever("saida_teste.csv", [])


class TestConfiguracaoAutomacao(unittest.TestCase):
    """Testes unitários para validação de ConfiguracaoAutomacao."""

    def test_configuracao_valida(self) -> None:
        """Deve criar configuração sem erros com dados válidos."""
        config = ConfiguracaoAutomacao(url="https://api.example.com", timeout=60)
        self.assertEqual(config.timeout, 60)

    def test_url_invalida(self) -> None:
        """Deve lançar ValueError para URL sem protocolo."""
        with self.assertRaises(ValueError):
            ConfiguracaoAutomacao(url="api.example.com")

    def test_timeout_negativo(self) -> None:
        """Deve lançar ValueError para timeout <= 0."""
        with self.assertRaises(ValueError):
            ConfiguracaoAutomacao(url="https://api.example.com", timeout=-1)


class TestProcessadorDados(unittest.TestCase):
    """Testes unitários para ProcessadorDados."""

    def setUp(self) -> None:
        self.processador = ProcessadorDados()

    def test_processar_usuario_ativo(self) -> None:
        """Deve retornar status 'sucesso' para usuário ativo."""
        usuario: UsuarioDict = {
            "id": 1, "nome": "Ana", "email": "ana@example.com", "ativo": True
        }
        resultado = self.processador.processar_usuario(usuario)
        self.assertEqual(resultado["status"], "sucesso")

    def test_processar_usuario_inativo(self) -> None:
        """Deve retornar status 'ignorado' para usuário inativo."""
        usuario: UsuarioDict = {
            "id": 2, "nome": "Bruno", "email": "bruno@example.com", "ativo": False
        }
        resultado = self.processador.processar_usuario(usuario)
        self.assertEqual(resultado["status"], "ignorado")


# =============================================================================
# EXECUÇÃO PRINCIPAL
# =============================================================================
def main() -> None:
    """
    Ponto de entrada principal da automação.

    Demonstra o uso integrado de todas as boas práticas.
    """
    logger.info("=== Iniciando Automação - BotCity Boas Práticas ===")

    # 1. Configuração centralizada + validação de entrada
    try:
        config = ConfiguracaoAutomacao(
            url=Config.API_URL,
            timeout=Config.API_TIMEOUT,
            retries=Config.API_RETRIES,
        )
        logger.info(f"Configuração carregada: URL={config.url}, timeout={config.timeout}s")
    except ValueError as e:
        logger.error(f"Configuração inválida: {e}")
        raise

    # 2. Processamento com TypedDict
    usuarios: list[UsuarioDict] = [
        {"id": 1, "nome": "Ana Paula", "email": "ana@botcity.dev", "ativo": True},
        {"id": 2, "nome": "Carlos Eduardo", "email": "carlos@botcity.dev", "ativo": False},
        {"id": 3, "nome": "Mariana Lima", "email": "mariana@botcity.dev", "ativo": True},
    ]

    def notificar(mensagem: str) -> None:
        """Callback de notificação após processamento."""
        logger.debug(f"[CALLBACK] {mensagem}")

    processador = ProcessadorDados(callback=notificar)
    resultados = processador.processar_lista(usuarios)

    # 3. Exportar resultados para CSV
    csv_processador = ProcessadorCSV()
    csv_processador.escrever("resultados.csv", resultados)  # type: ignore[arg-type]

    # 4. Consulta simulada ao banco
    ids_encontrados = buscar_usuarios_por_ids([1, 2, 3])
    logger.info(f"Usuários encontrados: {ids_encontrados}")

    # 5. Envio de notificação
    enviar_notificacao("equipe@botcity.dev", "Automação finalizada com sucesso")

    # 6. Executar testes unitários
    logger.info("=== Executando Testes Unitários ===")
    suite = unittest.TestLoader().loadTestsFromModule(__import__(__name__))
    runner = unittest.TextTestRunner(verbosity=2)
    runner.run(suite)

    logger.info("=== Automação Finalizada ===")


if __name__ == "__main__":
    main()