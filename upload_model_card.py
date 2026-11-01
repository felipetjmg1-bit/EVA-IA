"""Gera e publica o Model Card do EVA-IA no Hugging Face Hub."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from huggingface_hub import HfApi
from huggingface_hub.errors import HfHubHTTPError


MODEL_CARD = """---
language:
  - pt
license: proprietary
tags:
  - edge-ai
  - explainable-ai
metrics:
  - accuracy
---

# EVA-IA

## Visão geral

EVA-IA é um projeto de inteligência artificial explicável voltado à execução em dispositivos de borda. Este Model Card descreve informações iniciais do projeto; os detalhes técnicos devem ser atualizados conforme o modelo e as avaliações forem definidos.

## Uso pretendido

Descrever aqui os casos de uso previstos, o público-alvo e o contexto operacional do modelo.

## Limitações e considerações

- O modelo, os dados de treinamento e os resultados de avaliação ainda não foram especificados neste cartão.
- Não use resultados de desempenho até que sejam medidos e documentados em condições representativas.
- Avalie riscos, vieses, privacidade e requisitos de segurança antes de qualquer implantação.

## Avaliação

A métrica planejada inclui **accuracy**. O conjunto de avaliação, o protocolo e os resultados ainda precisam ser preenchidos; nenhum valor de desempenho é declarado neste cartão.

## Dados e treinamento

A documentação de dados, pré-processamento, treinamento e versões será adicionada quando essas informações estiverem disponíveis.

## Licença

Proprietária. O acesso e o uso do modelo estão sujeitos aos termos definidos pelos responsáveis pelo projeto.
"""


def load_settings(repo_id_override: str | None = None) -> tuple[str, str]:
    """Carrega as configurações sem sobrescrever variáveis já injetadas no ambiente."""
    env_file = Path(__file__).resolve().with_name(".env")
    load_dotenv(dotenv_path=env_file, override=False)

    token = os.getenv("HUGGINGFACE_TOKEN", "").strip()
    repo_id = (repo_id_override or os.getenv("HF_REPO_ID", "")).strip()
    if not token:
        raise ValueError(
            "HUGGINGFACE_TOKEN não foi definido. Configure-o no ambiente ou em "
            f"{env_file}; não compartilhe nem versione esse arquivo."
        )
    if not repo_id or "/" not in repo_id:
        raise ValueError(
            "Informe HF_REPO_ID no formato namespace/nome-do-modelo "
            "(ou use --repo-id)."
        )
    return token, repo_id


def build_model_card() -> str:
    """Retorna o Model Card em Markdown com metadados YAML do Hub."""
    return MODEL_CARD.strip() + "\n"


def publish_model_card(token: str, repo_id: str, revision: str = "main") -> str:
    """Garante a existência de um repositório privado e envia README.md."""
    api = HfApi(token=token)
    api.create_repo(
        repo_id=repo_id,
        repo_type="model",
        private=True,
        exist_ok=True,
    )

    repo = api.repo_info(repo_id=repo_id, repo_type="model")
    if not getattr(repo, "private", False):
        raise ValueError(
            f"O repositório {repo_id} não é privado. Por segurança, o upload foi "
            "interrompido; torne-o privado no Hugging Face antes de tentar novamente."
        )

    result = api.upload_file(
        path_or_fileobj=build_model_card().encode("utf-8"),
        path_in_repo="README.md",
        repo_id=repo_id,
        repo_type="model",
        revision=revision,
        commit_message="Add or update EVA-IA model card",
    )
    return str(getattr(result, "commit_url", "") or result)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Gera e publica README.md como Model Card no Hugging Face Hub."
    )
    parser.add_argument(
        "--repo-id",
        help="ID Hugging Face no formato namespace/nome (padrão: HF_REPO_ID).",
    )
    parser.add_argument(
        "--revision",
        default="main",
        help="Branch ou revisão de destino (padrão: main).",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        token, repo_id = load_settings(args.repo_id)
        commit_url = publish_model_card(token, repo_id, args.revision)
    except (ValueError, HfHubHTTPError) as exc:
        print(f"Erro ao publicar Model Card: {exc}", file=sys.stderr)
        return 1
    except Exception as exc:  # Erros inesperados da API/rede, sem exibir o token.
        print(
            f"Falha inesperada ({type(exc).__name__}): {exc}",
            file=sys.stderr,
        )
        return 1

    print(f"Model Card publicado em {repo_id} (revisão {args.revision}).")
    if commit_url:
        print(f"Commit: {commit_url}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
