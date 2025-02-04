LABELS_p = ['suhf', 'pbe', 'pbe02', ('pbe', 'p3', 0.25, 0.0, 0.40)]
LABELS_display = ['SUHF', 'SU-tPBE', 'SU-tPBE($\lambda,k$)', 'SU-tPBE($\lambda,c$)']

LABELS_p1 = ['suhf', 'pbe', ('pbe', 0.10, 2), ('pbe', 'p3', 0.25, 0.0, 0.40)]
LABELS_display1 = ['SUHF', 'SU-tPBE', 'SU-tPBE($\lambda=0.10,k=2$)', 'SU-tPBE($\lambda=0.25,c=0.40$)']
LABELS_p4 = ['suhf', 'pbe', ('pbe', 0.10, 2), ('pbe', 0.25, 2), ('pbe', 'p3', 0.25, 0.0, 0.40)]
LABELS_display4 = ['SUHF', 'SU-tPBE', 'SU-tPBE($\lambda=0.10,k=2$)', 'SU-tPBE($\lambda=0.25,k=2$)', 'SU-tPBE($\lambda=0.25,c=0.40$)']

LABELS_t = ['suhf', 'pbe', 'pbe02', ('pbe', 0.10, 2), ('pbe', 'p3', 0.25, 0.0, 0.40), 
            ('pbe', 't', 0.15, 0.0, -0.010),
            ('pbe', 't', 0.30, 0.0, -0.025), 
            # ('pbe', 't', 0.30, 0.0, -0.025),
            # ('pbe', 't', 0.30, 0.0, -0.005),
            # ('pbe', 't', 0.30, 0.10, -0.005),
            # ('pbe', 't', 0.30, 0.15, -0.005),
            # ('pbe', 't', 0.30, 0.20, -0.005),
            # ('pbe', 't', 0.30, 0.0, -0.020),
            # ('pbe', 't', 0.30, 0.05, -0.020),
            # ('pbe', 't', 0.30, 0.10, -0.020),
            # ('pbe', 't', 0.30, 0.15, -0.020),
            ]
# for h in np.arange(0.40, 0.40+0.01, 0.05):
#     for t in np.arange(-0.005, -0.030-0.001, -0.005):
#         for c in np.arange(-0.10, 0.25+0.01, 0.05):
#             LABELS_t.append(('pbe', 't', h, c, t))
LABELS_display_t = ['SUHF', 'SU-tPBE', 'SU-tPBE($\lambda,k$)','SU-tPBE($\lambda=0.10,k$)', 'SU-tPBE($\lambda,c$)',
                    'SU-tPBE($\lambda=0.15,\theta=-0.010$)', 
                    'SU-tPBE($\lambda=0.30,\theta=-0.025$)']

LABELS_t2 = ['suhf', 'pbe', ('pbe', 'p3', 0.25, 0.0, 0.40),
             ('pbe', 't', 0.25, 0.0, -0.025),
             ('pbe', 't', 0.30, 0.10, -0.010)
             ]
LABELS_display_t2 = ['SUHF', 'SU-tPBE', 'SU-tPBE($\lambda,c$)', 'SU-tPBE($\lambda,t=-0.025$)', 'SU-tPBE($\lambda,t=-0.010$)']

labelset = [[LABELS_p, LABELS_display], [LABELS_p1, LABELS_display1],
            [LABELS_t, LABELS_display_t], [LABELS_t2, LABELS_display_t2],
            [LABELS_p4, LABELS_display4]]