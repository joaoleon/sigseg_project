import pandas as pd
from app.models.objeto_roubado import ObjetoRoubado

def obter_estatisticas_monitoramento():
    """Retorna análises estatísticas e espaciais dos objetos roubados"""
    objetos = ObjetoRoubado.query.all()
    
    if not objetos:
        return {"erro": "Nenhuma ocorrência registrada"}, 404

    # 📌 Transformar os dados em um DataFrame do Pandas
    data = pd.DataFrame([obj.to_dict() for obj in objetos])

    # 📊 Estatísticas Temporais
    data["data_ocorrencia"] = pd.to_datetime(data["data_ocorrencia"])
    ocorrencias_por_mes = data["data_ocorrencia"].dt.to_period("M").value_counts().sort_index()
    ocorrencias_por_hora = data["hora_ocorrencia"].astype(str).str[:2].value_counts().sort_index()

    # 📊 Estatísticas Espaciais (Clusters e Mapa de Calor)
    localizacoes = data[["latitude", "longitude"]].dropna().values.tolist()

    # 📊 Estatísticas Gerais
    stats = {
        "total_ocorrencias": len(data),
        "tipo_mais_comum": data["tipo_objeto"].mode()[0] if not data["tipo_objeto"].empty else "N/A",
        "cidade_mais_afetada": data["cidade"].mode()[0] if not data["cidade"].empty else "N/A",
        "horario_mais_comum": data["hora_ocorrencia"].mode()[0] if not data["hora_ocorrencia"].empty else "N/A",
        "forma_subtracao_mais_comum": data["forma_subtracao"].mode()[0] if not data["forma_subtracao"].empty else "N/A",
        "meio_utilizado_mais_comum": data["meio_utilizado"].mode()[0] if not data["meio_utilizado"].empty else "N/A",
    }

    return {
        "stats": stats,
        "ocorrencias_por_mes": {str(k): v for k, v in ocorrencias_por_mes.to_dict().items()},
        "ocorrencias_por_hora": ocorrencias_por_hora.to_dict(),
        "localizacoes": localizacoes
    }
