"""Fixed GNU Radio experiments for authenticated DemoAccess sessions."""
from pathlib import Path
import yaml

VARIANT = 'pluto-tone-spectrum'
TONES = {'low': 25000, 'middle': 75000, 'high': 125000}

def demo_for_server_data(server_data):
    config = server_data.get('labsland_demo') or {}
    if isinstance(config, dict) and config.get('enabled') is True and config.get('relia_variant') == VARIANT:
        return {'variant': VARIANT, 'readonly': True, 'tones': TONES}
    return None

def flowgraphs(tone='middle'):
    if tone not in TONES:
        raise ValueError('Choose one of the three demo tones')
    graphs = {}
    for side, filename in (('receiver', 'tone_rx.grc'), ('transmitter', 'tone_tx.grc')):
        graph = yaml.safe_load((Path(__file__).parent / filename).read_text())
        if side == 'transmitter':
            for block in graph['blocks']:
                if block['id'] == 'analog_sig_source_x':
                    block['parameters']['freq'] = str(TONES[tone])
        graphs[side] = {'filename': filename, 'content': yaml.safe_dump(graph, sort_keys=False), 'type': 'grc'}
    return graphs
