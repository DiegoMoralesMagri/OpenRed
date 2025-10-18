@echo off
echo === OpenRed P2P Platform - Noeud 2 ===

REM Configuration variables d'environnement
set OPENRED_NODE_ID=web_node_2_batch
set OPENRED_SECTOR=secondary
set OPENRED_P2P_PORT=8082

echo Demarrage Noeud 2:
echo   Node ID: %OPENRED_NODE_ID%
echo   Secteur: %OPENRED_SECTOR%
echo   Port P2P: %OPENRED_P2P_PORT%
echo   Port Web: 8002
echo   Interface: http://localhost:8002

REM Lancement avec port web 8002
python -c "import uvicorn; uvicorn.run('web_api:app', host='0.0.0.0', port=8002, reload=False)"

pause