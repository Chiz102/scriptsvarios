import requests
import json 
import time
import pandas as pd


ENDPOINT = "https://www.cryptomkt.com/api/v1/landing/market_data/CLP"


HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36'}

def get_data_cryptomk(timeframe='day'):
    if not ENDPOINT: 
        print ("Error no ENDPOINT especificado")
        return None 
    
    try:
        response = requests.get(ENDPOINT, headers = HEADERS)
        response.raise_for_status()

        data = response,json()
        
        if data.get('status') == 'success':
            variations_data = data.get('data', {}).get('variations', {})
            crypto_data = variations_data.get(timeframe) #Obtener diccionario de datos de la cripto

            if not crypto_data:
                print(f"No se encontraron datos para el timeframe {timeframe}")
                return None 
    except requests.exceptions.HTTPError as http_err:
        print(f"Error HTTP: {http_err} - Código de estado: {response.status_code}")
        if response.content:
            print(f"Respuesta del servidor: {response.text}")
    except requests.exceptions.RequestException as req_err:
        print(f"Error en la petición: {req_err}")
    except json.JSONDecodeError as json_err:
        print(f"Error al decodificar JSON: {json_err}. Respuesta recibida:\n{response.text if 'response' in locals() else 'No response object'}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
    return None

if __name__ == "__main__":
    crypto_data_dict = get_data_cryptomk(timeframe='day')

    if crypto_data_dict:
        print(f"\nSe encontraron datos para {len(crypto_data_dict)} entradas (incluyendo posibles fiat).")

        processed_data_list = []
        for symbol, details in crypto_data_dict.items():
            if not symbol: # Ignorar la entrada con símbolo vacío que aparece en tu ejemplo
                continue

            # Filtrar para procesar solo criptomonedas (puedes quitar este if si quieres incluir fiat)
            if not details.get('is_crypto', False):
                # print(f"Ignorando moneda fiat: {details.get('name', symbol)}")
                continue

            try:
                new_price_str = details.get('new_price', '0')
                old_price_str = details.get('old_price', '0')

                # Convertir precios a float para cálculos. Manejar posibles errores.
                new_price = float(new_price_str)
                old_price = float(old_price_str)

                variation_24h = 0
                if old_price != 0: # Evitar división por cero
                    variation_24h = ((new_price - old_price) / old_price) * 100
                else:
                    variation_24h = float('inf') if new_price > 0 else 0 # Precio nuevo desde cero

                processed_data_list.append({
                    'Símbolo': symbol,
                    'Nombre': details.get('name', 'N/A'),
                    'Precio Actual (CLP)': new_price,
                    'Precio Anterior (CLP)': old_price,
                    'Variación 24h (%)': variation_24h,
                    'Ranking Cap.': details.get('cap_ranking', 'N/A'),
                    'Es Cripto': details.get('is_crypto')
                })
            except ValueError as ve:
                print(f"Error al convertir precios para {symbol}: {ve}. new_price='{new_price_str}', old_price='{old_price_str}'")
                continue # Saltar esta entrada si hay error en conversión de precios
            except Exception as ex:
                print(f"Error procesando {symbol}: {ex}")
                continue


        if not processed_data_list:
            print("No se procesaron datos de criptomonedas. Verifica la respuesta de la API o el filtro 'is_crypto'.")
        else:
            # --- Uso Opcional de Pandas para mostrar en una tabla ---
            df = pd.DataFrame(processed_data_list)

            print("\n--- Datos de Criptomonedas (Filtrado por 'is_crypto': true) ---")
            pd.set_option('display.max_rows', None)
            pd.set_option('display.max_colwidth', None)
            pd.set_option('display.width', 120) # Ajusta el ancho según tu consola

            # Intentar ordenar por Ranking Cap. si la columna existe y es numérica
            try:
                df['Ranking Cap.'] = pd.to_numeric(df['Ranking Cap.'], errors='coerce')
                df_sorted = df.sort_values(by='Ranking Cap.', ascending=True)
            except KeyError:
                print("Advertencia: La columna 'Ranking Cap.' no se generó, ordenando por Símbolo.")
                df_sorted = df.sort_values(by='Símbolo', ascending=True)
            except Exception as e_sort:
                print(f"Advertencia: No se pudo ordenar por 'Ranking Cap.' ({e_sort}), ordenando por Símbolo.")
                df_sorted = df.sort_values(by='Símbolo', ascending=True)


            print(df_sorted[['Símbolo', 'Nombre', 'Precio Actual (CLP)', 'Precio Anterior (CLP)', 'Variación 24h (%)', 'Ranking Cap.']])

            # Formatear la columna de variación para mejor lectura
            if 'Variación 24h (%)' in df_sorted.columns:
                df_sorted['Variación 24h (%)'] = df_sorted['Variación 24h (%)'].map('{:,.2f}%'.format)
            if 'Precio Actual (CLP)' in df_sorted.columns:
                 df_sorted['Precio Actual (CLP)'] = df_sorted['Precio Actual (CLP)'].map('{:,.2f}'.format) # Formato con comas y 2 decimales
            if 'Precio Anterior (CLP)' in df_sorted.columns:
                 df_sorted['Precio Anterior (CLP)'] = df_sorted['Precio Anterior (CLP)'].map('{:,.2f}'.format)


            print("\n--- Tabla Formateada ---")
            print(df_sorted[['Símbolo', 'Nombre', 'Precio Actual (CLP)', 'Precio Anterior (CLP)', 'Variación 24h (%)', 'Ranking Cap.']])

            # Guardar en CSV
            # df_sorted.to_csv('cryptomkt_variations_data.csv', index=False)
            # print("\nDatos guardados en cryptomkt_variations_data.csv")
    else:
        print("No se pudieron obtener o procesar los datos de CryptoMKT. Verifica la URL de la API y su respuesta.")