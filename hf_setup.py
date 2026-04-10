# -*- coding: utf-8 -*-
# Copyright (c) 2026 Felipe Marcos de Abreu Aquino. Todos os direitos reservados.
# Este código é propriedade intelectual exclusiva de Felipe Marcos de Abreu Aquino.

import os
from huggingface_hub import HfApi, create_repo

def setup_hf_repo(repo_id, token):
    """
    Cria o repositório no Hugging Face e faz o upload do Model Card.
    """
    api = HfApi()
    
    try:
        # Criar o repositório como privado
        create_repo(repo_id=repo_id, token=token, private=True, repo_type="model", exist_ok=True)
        print(f"Repositório {repo_id} criado ou já existente (Privado).")
        
        # Upload do README.md (Model Card)
        api.upload_file(
            path_or_fileobj="HUGGINGFACE_README.md",
            path_in_repo="README.md",
            repo_id=repo_id,
            token=token,
            repo_type="model"
        )
        print("Model Card (README.md) enviado com sucesso!")
        
    except Exception as e:
        print(f"Erro ao configurar Hugging Face: {e}")

if __name__ == "__main__":
    # Substitua pelo seu Token de Acesso do Hugging Face (Write)
    # HF_TOKEN = "seu_token_aqui"
    # REPO_ID = "seu_usuario/EVA-IA"
    print("Para rodar este script, instale: pip install huggingface_hub")
    print("E configure seu Token e Repo ID no código.")
