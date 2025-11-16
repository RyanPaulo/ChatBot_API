from typing import Optional, List, Union
from pydantic import BaseModel, Field, field_validator
from datetime import timedelta
import uuid

### ESQUEMA DE DADOS 'CURSO' ###

#Schema base com os campos que podem ser criados
class CursoBase(BaseModel):
    nome_curso: str
    periodo: int
    modalidade: List[str] = Field(default_factory=list)
    formacao: str
    descricao: str
    carga_horaria: Union[int, str, timedelta] = Field(..., description="Carga horária em horas (pode ser número, string ou timedelta)")

    @field_validator('carga_horaria', mode='before')
    @classmethod
    def parse_carga_horaria(cls, v):
        """
        Converte carga_horaria para timedelta.
        Aceita: int (horas), str (horas como string), timedelta, ou formato PostgreSQL INTERVAL (HH:MM:SS).
        """
        if isinstance(v, timedelta):
            return v
        if v is None:
            return None
        
        # Se for string, pode ser formato PostgreSQL INTERVAL (ex: "440:00:00" ou "18 days 8:00:00")
        if isinstance(v, str):
            # Verifica se é formato PostgreSQL INTERVAL (HH:MM:SS ou HH:MM:SS.microseconds)
            if ':' in v:
                try:
                    # Formato: "440:00:00" ou "18 days 8:00:00"
                    parts = v.split()
                    if len(parts) > 1 and 'days' in parts:
                        # Formato: "18 days 8:00:00"
                        days = int(parts[0])
                        time_part = parts[2] if len(parts) > 2 else "0:0:0"
                        h, m, s = map(int, time_part.split(':'))
                        return timedelta(days=days, hours=h, minutes=m, seconds=s)
                    else:
                    
                        time_parts = v.split(':')
                        if len(time_parts) == 3:
                            h = int(time_parts[0])
                            m = int(time_parts[1])
                            # Pode ter microssegundos: "00.123456"
                            s_part = time_parts[2].split('.')
                            s = int(s_part[0])
                            microseconds = int(float('0.' + s_part[1]) * 1000000) if len(s_part) > 1 else 0
                            return timedelta(hours=h, minutes=m, seconds=s, microseconds=microseconds)
                except (ValueError, IndexError):
                    pass
            
            # Se não for formato INTERVAL, tenta converter para int (horas)
            try:
                horas = int(v)
                return timedelta(hours=horas)
            except ValueError:
                raise ValueError(f"Carga horária inválida: {v}. Deve ser um número (horas), timedelta ou formato INTERVAL (HH:MM:SS).")
        
        # Se for int, converte para horas
        try:
            horas = int(v)
            return timedelta(hours=horas)
        except (ValueError, TypeError):
            raise ValueError(f"Carga horária inválida: {v}. Deve ser um número (horas), timedelta ou formato INTERVAL (HH:MM:SS).")

# Schema para a criação da tabela 'Curso'
class CursoCreate(CursoBase):
    pass

# Para representar um registro completo do banco de dados
class Curso(CursoBase):
    id_curso: uuid.UUID

    class Config:
        from_attributes = True


# Schema para atualização do Curso
class CursoUpadate(BaseModel):
    nome_curso: Optional[str] = None
    periodo: Optional[int] = None
    modalidade: Optional[List[str]] = Field(default_factory=list)
    formacao: Optional[str] = None
    descricao: Optional[str] = None
    carga_horaria: Optional[Union[int, str, timedelta]] = Field(None, description="Carga horária em horas (pode ser número, string ou timedelta)")

    @field_validator('carga_horaria', mode='before')
    @classmethod
    def parse_carga_horaria_update(cls, v):
        """
        Converte carga_horaria para timedelta.
        Aceita: int (horas), str (horas como string), timedelta, ou formato PostgreSQL INTERVAL (HH:MM:SS).
        """
        if v is None:
            return None
        if isinstance(v, timedelta):
            return v
        
        # Se for string, pode ser formato PostgreSQL INTERVAL (ex: "440:00:00" ou "18 days 8:00:00")
        if isinstance(v, str):
            # Verifica se é formato PostgreSQL INTERVAL (HH:MM:SS ou HH:MM:SS.microseconds)
            if ':' in v:
                try:
                    # Formato: "440:00:00" ou "18 days 8:00:00"
                    parts = v.split()
                    if len(parts) > 1 and 'days' in parts:
                        # Formato: "18 days 8:00:00"
                        days = int(parts[0])
                        time_part = parts[2] if len(parts) > 2 else "0:0:0"
                        h, m, s = map(int, time_part.split(':'))
                        return timedelta(days=days, hours=h, minutes=m, seconds=s)
                    else:
                        # Formato: "440:00:00" ou "440:00:00.123456" (horas:minutos:segundos[.microsegundos])
                        time_parts = v.split(':')
                        if len(time_parts) == 3:
                            h = int(time_parts[0])
                            m = int(time_parts[1])
                            # Pode ter microssegundos: "00.123456"
                            s_part = time_parts[2].split('.')
                            s = int(s_part[0])
                            microseconds = int(float('0.' + s_part[1]) * 1000000) if len(s_part) > 1 else 0
                            return timedelta(hours=h, minutes=m, seconds=s, microseconds=microseconds)
                except (ValueError, IndexError):
                    pass
            
            # Se não for formato INTERVAL, tenta converter para int (horas)
            try:
                horas = int(v)
                return timedelta(hours=horas)
            except ValueError:
                raise ValueError(f"Carga horária inválida: {v}. Deve ser um número (horas), timedelta ou formato INTERVAL (HH:MM:SS).")
        
        # Se for int, converte para horas
        try:
            horas = int(v)
            return timedelta(hours=horas)
        except (ValueError, TypeError):
            raise ValueError(f"Carga horária inválida: {v}. Deve ser um número (horas), timedelta ou formato INTERVAL (HH:MM:SS).")