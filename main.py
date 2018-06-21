# -*- coding: utf-8 -*-

import json
import re
import pandas as pd
import locale

from flask import Flask, jsonify, make_response
from flask import request


app = Flask(__name__)

locale.setlocale(locale.LC_ALL, 'es_ES.utf8')

@app.route('/test', methods=['POST', 'GET'])
def get_test():
    print("Request received")
    print(request.json)
    return jsonify('{"Status" : "OK"}'), 200


# endpoint for the web hook
@app.route('/', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)
    print(json.dumps(req, indent=4))
    try:
        action = req.get('queryResult').get('action')
    except AttributeError:
        return 'json error'

    print('the action is ' + action)
    if action == 'action.alda.loan.application':
        print('Executing action.alda.loan.application')
        return best_lenders(req)
    if action == 'action.dni.validation':
        return validateDni(req)
    if action == 'action.phone.validation':
        return validateTlf(req)
    if action == 'action.email.validation':
        return validateEmail(req)
    return req


def best_lenders(req):
    try:
        amount = req.get('queryResult').get('parameters').get('amount').get('number')
    except AttributeError:
        print ('amount not recognized')
        if req.get('queryResult').get('parameters').get('amount') != '':
            print ('amount filled but not recognized')
            return make_response(jsonify({'fulfillmentText': 'No te he entendido...',
                                          'fulfillmentMessages': [
                                              {
                                                  "quickReplies": {
                                                      "title": 'Puedo ayudarte a encontrar el mejor préstamo, a invertir, con la declaración de la renta y a saber si estás en Asnef',
                                                      'quickReplies': [
                                                          'Necesito un préstamo',
                                                          'Quiero invertir',
                                                          'Declaración renta',
                                                          '¿Estoy en Asnef?',
                                                          'No me interesa'
                                                      ]
                                                  }
                                              }
                                          ]}))
        else:
            print('amount is empty and not recognized')
            return 'amount not recognized'

    if amount < 50:
        print('Amount under 50 euros')
        return make_response(jsonify({'fulfillmentText': 'Ninguna entidad ofrece menos de 50€...',
                                      'fulfillmentMessages': [
                                          {
                                              "quickReplies": {
                                                  "title": 'Ninguna empresa ofrece menos de 50€...',
                                                  'quickReplies': [
                                                      'Quiero 50€',
                                                      'Quiero más de 50€',
                                                      'Ayúdame'
                                                  ]
                                              }
                                          }
                                      ]}))
    if amount <= 300:
        print('Amount between 50 and 300')
        return make_response(jsonify({'fulfillmentText': '',
                                      'fulfillmentMessages': [
                                          {
                                              'text': {
                                                  'text': [
                                                      '¡Genial! Te muestro los mejores préstamos que ofrecen ' + str(
                                                          int(amount)) + '€ ordenados por precio (TAE)'
                                                  ]
                                              }
                                          },
                                          {
                                              'card': {
                                                  'title': 'Vivus',
                                                  'subtitle': 'Hasta 300€ 30 días \n 30 días gratis \n Sin comisiones',
                                                  'imageUri': 'https://s3-eu-west-1.amazonaws.com/aldachatbot/vivus.png',
                                                  'buttons': [
                                                      {
                                                          'text': 'Seleccionar',
                                                          'postback': 'https://www.vivus.es/'
                                                      },
                                                      {
                                                          'text': 'Más información',
                                                          'postback': 'https://www.vivus.es/'
                                                      }
                                                  ]

                                              }
                                          },
                                          {
                                              'card': {
                                                  'title': 'Wonga',
                                                  'subtitle': 'Hasta 300€ 60 días \n 15 días gratis \n Sin comisiones',
                                                  'imageUri': 'https://s3-eu-west-1.amazonaws.com/aldachatbot/wonga.png',
                                                  'buttons': [
                                                      {
                                                          'text': 'Seleccionar',
                                                          'postback': 'https://www.wonga.es/'
                                                      },
                                                      {
                                                          'text': 'Más información',
                                                          'postback': 'https://www.wonga.es/'
                                                      }
                                                  ]

                                              }
                                          },
                                          {
                                              'card': {
                                                  'title': 'Qué Bueno!',
                                                  'subtitle': 'Hasta 300€ 34 días \n Sin comisiones',
                                                  'imageUri': 'https://s3-eu-west-1.amazonaws.com/aldachatbot/quebueno.png',
                                                  'buttons': [
                                                      {
                                                          'text': 'Seleccionar',
                                                          'postback': 'https://www.quebueno.es/'
                                                      },
                                                      {
                                                          'text': 'Más información',
                                                          'postback': 'https://www.quebueno.es/'
                                                      }
                                                  ]

                                              }
                                          },
                                          {
                                              "quickReplies": {
                                                  "title": 'Préstamos por importes tan pequeños tienen unos intereses muy elevados. En ocasiones, el mejor préstamo es el que no se pide',
                                                  'quickReplies': [
                                                      '¡Gracias!',
                                                      '¿TAE?',
                                                      'Estoy en ASNEF',
                                                      '¿Historial crediticio?',
                                                      'Más ayuda'
                                                  ]
                                              }
                                          }
                                      ],
                                      }
                                     )
                             )

    if amount <= 50000:
        print('Amount between 300 and 50.000€')

        response = []

        response.append({'text': {
                              'text': [
                                  '¡Genial! A continuación te muestro los mejores préstamos que te ofrecen ' +
                                  '{:n}'.format(amount) + '€ ordenados por precio (TAE)'
                              ]}})

        lenders_df = pd.read_csv('https://s3-eu-west-1.amazonaws.com/aldachatbot/lenders.csv', delimiter=";", header=0)

        for index, row in lenders_df.iterrows():
            print("Checking " + row["Lender"])
            if row['Min_Amt'] <= amount <= row['Max_Amt']:
                print('Including ' + row['Lender'])
                response.append({
                    'card': {
                        'title': row['Lender'],
                        'subtitle': 'Hasta ' + '{:n}'.format(row['Max_Amt']) + "€ \n TAE desde "
                                    + str(row['Min_TAE']) + "% \n " + row['Subtitle'],
                        'imageUri': row['Image_url'],
                        'buttons': [
                            {
                                'text': 'Seleccionar',
                                'postback': row['Url']
                            },
                            {
                                'text': 'Más información',
                                'postback': row['Url']
                            }]}})

        response.append({
            'quickReplies': {
                'title': 'Además de estas opciones, es posible que tu banco te ofrezca un préstamo preconcedido: este tipo de préstamo es el más rápido pero también es el más caro!',
                'quickReplies': [
                    '¡Gracias!',
                    '¿TAE?'
                ]
            }
        })

        return make_response(jsonify({'fulfillmentMessages': response}))

    if amount > 60000:
        print('Amount above 60.000€')
        return make_response(
            jsonify({'fulfillmentText': 'Ninguna entidad ofrece más de 60.000€ sin un aval hipotecario',
                     'fulfillmentMessages': [
                         {
                             'quickReplies': {
                                 'title': 'Ninguna entidad ofrece más de 60.000€ sin un aval hipotecario',
                                 'quickReplies': [
                                     'Quiero 60.000€',
                                     'Quiero menos de 60.000€',
                                     'Ayúdame'
                                 ]
                             }
                         }
                     ]}))


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8088)
