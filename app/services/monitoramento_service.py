import pandas as pd
from sqlalchemy.orm import sessionmaker
from app.models.objeto_roubado import ObjetoRoubado
from app.extensions import db

def obter_estatisticas_monitoramento():
    """Retorna análises estatísticas e espaciais dos objetos roubados"""

    # 📌 Corrigido: Criando sessão com `sessionmaker`
    Session = sessionmaker(bind=db.engine)
    session = Session()

    objetos = session.query(
        ObjetoRoubado.data_ocorrencia,
        ObjetoRoubado.hora_ocorrencia,
        ObjetoRoubado.tipo_objeto,
        ObjetoRoubado.forma_subtracao,
        ObjetoRoubado.meio_utilizado,
        ObjetoRoubado.cidade,
        ObjetoRoubado.latitude,
        ObjetoRoubado.longitude
    ).all()
    
    session.close()

    if not objetos:
        return {"erro": "Nenhuma ocorrência registrada"}, 404

    # 📌 Transformar os dados em um DataFrame do Pandas
    data = pd.DataFrame(objetos, columns=[
        "data_ocorrencia", "hora_ocorrencia", "tipo_objeto",
        "forma_subtracao", "meio_utilizado", "cidade", "latitude", "longitude"
    ])

    # 📊 Estatísticas Temporais
    if not data.empty:
        data["data_ocorrencia"] = pd.to_datetime(data["data_ocorrencia"], errors="coerce")
        data["hora_ocorrencia"] = data["hora_ocorrencia"].astype(str).str[:2]

        ocorrencias_por_mes = data["data_ocorrencia"].dt.to_period("M").value_counts().sort_index().to_dict()
        ocorrencias_por_hora = data["hora_ocorrencia"].value_counts().sort_index().to_dict()
        tipo_mais_comum = data["tipo_objeto"].value_counts().to_dict()
    else:
        ocorrencias_por_mes, ocorrencias_por_hora, tipo_mais_comum = {}, {}, {}

    # 📊 Estatísticas Espaciais (Clusters e Mapa de Calor)
    localizacoes = data[["latitude", "longitude"]].dropna().drop_duplicates().to_dict("records")

    # 📊 Estatísticas Gerais
    stats = {
        "total_ocorrencias": len(data),
        "tipo_mais_comum": data["tipo_objeto"].mode()[0] if not data["tipo_objeto"].isna().all() else "Desconhecido",
        "cidade_mais_afetada": data["cidade"].mode()[0] if not data["cidade"].isna().all() else "Desconhecido",
        "horario_mais_comum": data["hora_ocorrencia"].mode()[0] if not data["hora_ocorrencia"].isna().all() else "Desconhecido",
        "forma_subtracao_mais_comum": data["forma_subtracao"].mode()[0] if not data["forma_subtracao"].isna().all() else "Desconhecido",
        "meio_utilizado_mais_comum": data["meio_utilizado"].mode()[0] if not data["meio_utilizado"].isna().all() else "Desconhecido",
    }

    return {
        "stats": stats,
        "ocorrencias_por_mes": {str(k): v for k, v in ocorrencias_por_mes.items()},
        "ocorrencias_por_hora": ocorrencias_por_hora,
        "tipo_mais_comum": tipo_mais_comum,
        "localizacoes": localizacoes
    }
