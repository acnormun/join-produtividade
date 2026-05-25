import csv
import re
import unicodedata
from typing import Optional

import pandas as pd


class ProcessadorTabelas:
    """Processa tabelas de referência, CAIXA e VOTO para adicionar colunas de busca."""
    
    def __init__(
        self,
        coluna_busca: str = "numeroProcesso",
        referencia_coluna_indice: int = 0,
        caixa_coluna_indice: int = 2,
        voto_coluna_indice: int = 2,
    ):
        """
        Args:
            coluna_busca: Nome da coluna usada como identificador único para busca
        """
        self.coluna_busca = coluna_busca
        self.referencia_coluna_indice = referencia_coluna_indice
        self.caixa_coluna_indice = caixa_coluna_indice
        self.voto_coluna_indice = voto_coluna_indice
        self.referencia_df = None
        self.caixa_df = None
        self.voto_df = None
        self.resultado_df = None
        self.votos_sem_referencia_df = None
        self.coluna_referencia = None

    def _normalizar_nome_coluna(self, coluna: str) -> str:
        texto = unicodedata.normalize("NFKD", str(coluna))
        texto = "".join(char for char in texto if not unicodedata.combining(char))
        texto = texto.lower().replace("º", "o").replace("°", "o")
        return re.sub(r"[^a-z0-9]", "", texto)

    def _encontrar_coluna_busca(self, df: pd.DataFrame) -> Optional[str]:
        aliases = {
            self._normalizar_nome_coluna(self.coluna_busca),
            "numeroprocesso",
            "noprocesso",
            "nprocesso",
            "nroprocesso",
            "numprocesso",
            "processo",
        }

        for coluna in df.columns:
            if self._normalizar_nome_coluna(coluna) in aliases:
                return coluna
        return None

    def _validar_indice_coluna(self, df: pd.DataFrame, indice: int, nome_tabela: str) -> None:
        if indice >= len(df.columns):
            letra = chr(ord("A") + indice) if indice < 26 else str(indice + 1)
            raise ValueError(f"{nome_tabela} deve ter a coluna {letra}")

    def _normalizar_valores_busca(self, serie: pd.Series) -> pd.Series:
        return serie.fillna("").astype(str).str.strip()

    def _detectar_separador(self, caminho: str, encoding: str) -> Optional[str]:
        """Detecta separador CSV comum em arquivos exportados por Excel/sistemas."""
        with open(caminho, "r", encoding=encoding, newline="") as arquivo:
            amostra = arquivo.read(8192)

        try:
            return csv.Sniffer().sniff(amostra, delimiters=";,\t|").delimiter
        except csv.Error:
            return None

    def _ler_csv(self, caminho: str) -> pd.DataFrame:
        """Lê CSV com detecção de encoding e separador."""
        encodings = ("utf-8-sig", "utf-8", "latin1")
        separadores_padrao = (";", ",", "\t", "|")
        ultimo_erro = None

        for encoding in encodings:
            try:
                separador_detectado = self._detectar_separador(caminho, encoding)
            except UnicodeDecodeError as e:
                ultimo_erro = e
                continue

            separadores = []
            if separador_detectado:
                separadores.append(separador_detectado)
            separadores.extend(sep for sep in separadores_padrao if sep not in separadores)

            for separador in separadores:
                try:
                    df = pd.read_csv(
                        caminho,
                        sep=separador,
                        encoding=encoding,
                        engine="python",
                        dtype=str,
                        keep_default_na=False,
                    )
                    df.columns = df.columns.str.strip()
                    return df
                except (UnicodeDecodeError, pd.errors.ParserError) as e:
                    ultimo_erro = e

        raise ultimo_erro or ValueError("Não foi possível ler o arquivo CSV")
    
    def carregar_referencia(self, caminho: str) -> bool:
        """Carrega tabela de referência. Retorna True se sucesso."""
        try:
            self.referencia_df = self._ler_csv(caminho)
            self._validar_indice_coluna(
                self.referencia_df,
                self.referencia_coluna_indice,
                "Tabela de referencia",
            )
            self.coluna_referencia = self.referencia_df.columns[self.referencia_coluna_indice]
            if self.coluna_referencia is None:
                raise ValueError(f"Coluna '{self.coluna_busca}' não encontrada na tabela de referência")
            return True
        except Exception as e:
            raise Exception(f"Erro ao carregar tabela de referência: {e}")
    
    def carregar_caixa(self, caminho1: str, caminho2: Optional[str] = None) -> bool:
        """Carrega planilhas CAIXA. A segunda planilha e opcional."""
        try:
            caixa1 = self._ler_csv(caminho1)
            
            # Validar se coluna C existe (considerando índice 2)
            self._validar_indice_coluna(caixa1, self.caixa_coluna_indice, "Planilha CAIXA 1")
            caixas = [caixa1]
            if caminho2:
                caixa2 = self._ler_csv(caminho2)
                self._validar_indice_coluna(caixa2, self.caixa_coluna_indice, "Planilha CAIXA 2")
                caixas.append(caixa2)
            
            # Concatenar as planilhas CAIXA disponiveis
            self.caixa_df = pd.concat(caixas, ignore_index=True)
            return True
        except Exception as e:
            raise Exception(f"Erro ao carregar planilhas CAIXA: {e}")
    
    def carregar_voto(self, caminho: str) -> bool:
        """Carrega tabela VOTO. Retorna True se sucesso."""
        try:
            self.voto_df = self._ler_csv(caminho)
            self._validar_indice_coluna(self.voto_df, self.voto_coluna_indice, "Tabela VOTO")
            return True
        except Exception as e:
            raise Exception(f"Erro ao carregar tabela VOTO: {e}")
    
    def adicionar_colunas_busca(self) -> bool:
        """Adiciona colunas 'Ta na caixa?' e 'Tem voto?' à tabela de referência."""
        if self.referencia_df is None or self.caixa_df is None or self.voto_df is None:
            raise ValueError("Nem todas as tabelas foram carregadas")
        
        try:
            # Criar cópia para não modificar original
            resultado = self.referencia_df.copy()
            
            # Obter coluna C (índice 2) das tabelas de busca
            referencia_coluna_busca = self._normalizar_valores_busca(
                resultado.iloc[:, self.referencia_coluna_indice]
            )
            referencia_valores_busca = set(referencia_coluna_busca)
            caixa_valores_busca = set(
                self._normalizar_valores_busca(self.caixa_df.iloc[:, self.caixa_coluna_indice])
            )
            voto_coluna_normalizada = self._normalizar_valores_busca(
                self.voto_df.iloc[:, self.voto_coluna_indice]
            )
            voto_valores_busca = set(voto_coluna_normalizada)
            caixa_coluna_busca = pd.Series(list(caixa_valores_busca))
            voto_coluna_busca = pd.Series(list(voto_valores_busca))
            
            # Adicionar coluna "Ta na caixa?"
            resultado["Ta na caixa?"] = referencia_coluna_busca.apply(
                lambda x: "SIM" if x in caixa_coluna_busca.values else "NÃO"
            )
            
            # Adicionar coluna "Tem voto?"
            resultado["Tem voto?"] = referencia_coluna_busca.apply(
                lambda x: "SIM" if x in voto_coluna_busca.values else "NÃO"
            )
            
            self.resultado_df = resultado
            votos_sem_referencia_mask = (
                voto_coluna_normalizada.ne("")
                & ~voto_coluna_normalizada.isin(referencia_valores_busca)
            )
            self.votos_sem_referencia_df = self.voto_df.loc[votos_sem_referencia_mask].copy()
            return True
        except Exception as e:
            raise Exception(f"Erro ao adicionar colunas de busca: {e}")
    
    def exportar_excel(self, caminho_saida: str) -> bool:
        """Exporta resultado em Excel. Retorna True se sucesso."""
        if self.resultado_df is None:
            raise ValueError("Nenhum resultado disponível para exportar")
        
        try:
            with pd.ExcelWriter(caminho_saida, engine="openpyxl") as writer:
                self.resultado_df.to_excel(writer, index=False, sheet_name="Resultado")
                if self.votos_sem_referencia_df is not None:
                    self.votos_sem_referencia_df.to_excel(
                        writer,
                        index=False,
                        sheet_name="Votos sem referencia",
                    )
            return True
        except Exception as e:
            raise Exception(f"Erro ao exportar para Excel: {e}")
    
    def processar_completo(self, ref_path: str, caixa1_path: str, caixa2_path: Optional[str],
                          voto_path: str, output_path: str) -> bool:
        """Executa pipeline completo de processamento."""
        self.carregar_referencia(ref_path)
        self.carregar_caixa(caixa1_path, caixa2_path)
        self.carregar_voto(voto_path)
        self.adicionar_colunas_busca()
        self.exportar_excel(output_path)
        return True
    
    def get_resultado(self) -> Optional[pd.DataFrame]:
        """Retorna dataframe com resultado."""
        return self.resultado_df

    def get_votos_sem_referencia(self) -> Optional[pd.DataFrame]:
        """Retorna votos cujo processo nao existe na tabela de referencia."""
        return self.votos_sem_referencia_df
