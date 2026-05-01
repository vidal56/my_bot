#!/usr/bin/env python3
"""
Visualizador de distância LiDAR 1D no terminal
Lê o tópico /scan e exibe uma barra visual em tempo real
"""

import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan
from rclpy.qos import QoSProfile, ReliabilityPolicy, DurabilityPolicy
import os
import sys

# ── Configurações ────────────────────────────────────────────
MAX_DIST   = 5.0    # distância máxima esperada (metros)
BAR_WIDTH  = 50     # largura da barra em caracteres
TOPIC      = '/scan'

# ── Cores ANSI ───────────────────────────────────────────────
RED    = '\033[91m'
YELLOW = '\033[93m'
GREEN  = '\033[92m'
CYAN   = '\033[96m'
BOLD   = '\033[1m'
RESET  = '\033[0m'

def distancia_para_cor(dist: float) -> str:
    if dist < 0.5:
        return RED
    elif dist < 1.5:
        return YELLOW
    else:
        return GREEN

def desenhar_barra(dist: float) -> str:
    proporcao = min(dist / MAX_DIST, 1.0)
    preenchido = int(proporcao * BAR_WIDTH)
    vazio = BAR_WIDTH - preenchido

    cor = distancia_para_cor(dist)
    barra = f"{cor}{'█' * preenchido}{'░' * vazio}{RESET}"
    return barra

def limpar_tela():
    os.system('clear')

class LidarVisual(Node):
    def __init__(self):
        super().__init__('lidar_visual')
        qos = QoSProfile(
            depth=10,
            reliability=ReliabilityPolicy.BEST_EFFORT,
            durability=DurabilityPolicy.VOLATILE
        )
        self.subscription = self.create_subscription(
            LaserScan,
            TOPIC,
            self.callback,
            qos
        )
        self.ultima_dist = None
        self.contagem = 0
        limpar_tela()
        print(f"{BOLD}{CYAN}🔭 Visualizador LiDAR 1D — aguardando dados em {TOPIC}...{RESET}\n")

    def callback(self, msg: LaserScan):
        self.contagem += 1

        # Para LiDAR 1D pega só o primeiro (e único) raio
        ranges = msg.ranges
        if not ranges:
            return

        # Filtra valores inválidos (inf / nan / 0)
        validos = [r for r in ranges if 0.01 < r < msg.range_max]
        if not validos:
            dist = 0.0
        else:
            dist = min(validos)   # pega a menor leitura válida

        self.ultima_dist = dist
        self.renderizar(dist, msg.range_min, msg.range_max)

    def renderizar(self, dist: float, d_min: float, d_max: float):
        cor = distancia_para_cor(dist)
        barra = desenhar_barra(dist)

        # Aviso de proximidade
        if dist < 0.3:
            alerta = f"  {RED}{BOLD}⚠️  MUITO PERTO!{RESET}"
        elif dist < 0.5:
            alerta = f"  {YELLOW}⚡ Atenção{RESET}"
        else:
            alerta = ""

        # Monta o display
        linhas = [
            f"\033[H",   # move cursor para o topo (sem flicker)
            f"{BOLD}{CYAN}╔══════════════════════════════════════════════════╗{RESET}",
            f"{BOLD}{CYAN}║       🔭  Visualizador LiDAR 1D — ROS2          ║{RESET}",
            f"{BOLD}{CYAN}╚══════════════════════════════════════════════════╝{RESET}",
            "",
            f"  Tópico : {CYAN}{TOPIC}{RESET}",
            f"  Leituras recebidas : {self.contagem}",
            f"  Range  : {d_min:.2f}m  →  {d_max:.2f}m",
            "",
            f"  {BOLD}Distância:{RESET}",
            f"  {cor}{BOLD}{dist:6.3f} m{RESET}{alerta}",
            "",
            f"  0 m {'':2} {barra} {MAX_DIST} m",
            "",
            f"  {GREEN}█ > 1.5m{RESET}   {YELLOW}█ 0.5–1.5m{RESET}   {RED}█ < 0.5m{RESET}",
            "",
            f"  {BOLD}Ctrl+C{RESET} para sair",
        ]

        sys.stdout.write('\n'.join(linhas) + '\n')
        sys.stdout.flush()


def main():
    rclpy.init()
    node = LidarVisual()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print(f"\n\n{CYAN}Encerrando visualizador. Até mais! 👋{RESET}\n")
    finally:
        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()