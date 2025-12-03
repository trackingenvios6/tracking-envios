"""
Script de prueba para visualizar los nuevos menús con colores.
Ejecutar: python test_menus.py
"""
from ui.menus import (
    menu_principal,
    menu_compartir,
    menu_local,
    menu_continuar,
    menu_plataforma_compartir
)
import time

def main():
    print("\n" + "="*80)
    print("PREVIEW DE MENÚS CON RICH - Proyecto Piki")
    print("="*80)
    
    input("\n▶️  Presiona ENTER para ver el Menú Principal...")
    menu_principal()
    
    time.sleep(1.5)
    
    input("\n▶️  Presiona ENTER para ver el Menú Compartir...")
    menu_compartir()
    
    time.sleep(1.5)
    
    input("\n▶️  Presiona ENTER para ver el Menú Local...")
    menu_local()
    
    time.sleep(1.5)
    
    input("\n▶️  Presiona ENTER para ver el Menú Continuar...")
    menu_continuar()
    
    time.sleep(1.5)
    
    input("\n▶️  Presiona ENTER para ver el Menú Plataforma...")
    menu_plataforma_compartir()
    
    print("\n" + "="*80)
    print("✨ FIN DEL PREVIEW - ¡Los menús se ven increíbles!")
    print("="*80 + "\n")

if __name__ == "__main__":
    main()
