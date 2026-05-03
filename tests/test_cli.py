"""Tests for PLATO CLI argument parsing."""

import pytest
import sys
from io import StringIO
from unittest.mock import patch, MagicMock


class MockArgs:
    """Mock namespace for argparse."""
    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)


def test_phi_command_parses():
    """Test phi command argument parsing."""
    from plato_cli import cmd_phi
    with patch('plato_cli.RoomPhi') as mock_phi:
        mock_instance = MagicMock()
        mock_instance.compute_for_room.return_value = {
            'room': 'test_room',
            'phi': 0.5,
            'level': 'conscious',
            'tile_count': 10,
            'status': 'active'
        }
        mock_phi.return_value = mock_instance
        args = MockArgs(room='test_room')
        # Should not raise
        cmd_phi(args)


def test_phi_all_command():
    """Test phi all rooms scanning."""
    from plato_cli import cmd_phi
    with patch('plato_cli.RoomPhi') as mock_phi:
        mock_instance = MagicMock()
        mock_instance.scan_all_rooms.return_value = [
            {'room': 'room1', 'phi': 0.5, 'level': 'low', 'tile_count': 5},
            {'room': 'room2', 'phi': 0.8, 'level': 'high', 'tile_count': 20},
        ]
        mock_phi.return_value = mock_instance
        args = MockArgs(room='all')
        cmd_phi(args)


def test_attention_without_agent():
    """Test attention command without agent (summary)."""
    from plato_cli import cmd_attention
    with patch('plato_cli.AttentionTracker') as mock_tracker:
        mock_instance = MagicMock()
        mock_instance.get_attention_summary.return_value = {
            'total_tiles': 42,
            'agents_tracking': 3,
            'by_agent': {'oracle1': 20, 'kimi-cli': 22}
        }
        mock_tracker.return_value = mock_instance
        args = MockArgs(agent=None)
        cmd_attention(args)


def test_attention_with_agent():
    """Test attention command with specific agent."""
    from plato_cli import cmd_attention
    with patch('plato_cli.AttentionTracker') as mock_tracker:
        mock_instance = MagicMock()
        mock_instance.get_agent_attention.return_value = [
            {'answer': 'tile 1'},
            {'answer': 'tile 2'},
        ]
        mock_tracker.return_value = mock_instance
        args = MockArgs(agent='oracle1')
        cmd_attention(args)


def test_meta_without_tile_id():
    """Test meta command without tile-id (summary)."""
    from plato_cli import cmd_meta
    with patch('plato_cli.MetaTileEngine') as mock_meta:
        mock_instance = MagicMock()
        mock_instance.get_meta_level_summary.return_value = {
            'level_1': 10,
            'level_2': 5,
            'level_3': 2
        }
        mock_meta.return_value = mock_instance
        args = MockArgs(tile_id=None)
        cmd_meta(args)


def test_meta_with_tile_id():
    """Test meta command with specific tile-id."""
    from plato_cli import cmd_meta
    with patch('plato_cli.MetaTileEngine') as mock_meta:
        mock_instance = MagicMock()
        mock_instance.get_meta_tiles_for.return_value = [
            {'meta_level': 1, 'answer': 'meta tile content'},
        ]
        mock_meta.return_value = mock_instance
        args = MockArgs(tile_id='tile_123')
        cmd_meta(args)


def test_surprise_report():
    """Test surprise report subcommand."""
    from plato_cli import cmd_surprise
    with patch('plato_cli.SurpriseDetector') as mock_detector:
        mock_instance = MagicMock()
        mock_instance.report_outcome.return_value = {
            'surprise': 0.9,
            'accumulated_surprise': 1.5,
            'threshold_exceeded': True
        }
        mock_detector.return_value = mock_instance
        args = MockArgs(
            subcmd='report',
            positional=['oracle1', 'deploy', 'success', 'failed'],
            domain=None
        )
        cmd_surprise(args)


def test_surprise_status():
    """Test surprise status subcommand."""
    from plato_cli import cmd_surprise
    with patch('plato_cli.SurpriseDetector') as mock_detector:
        mock_instance = MagicMock()
        mock_instance.get_fleet_surprise.return_value = {
            'total_surprise': 2.5,
            'average_surprise': 0.5,
            'critical_agents': ['oracle1', 'kimi-cli']
        }
        mock_detector.return_value = mock_instance
        args = MockArgs(subcmd='status', positional=[], domain=None)
        cmd_surprise(args)


def test_fflearn_positive():
    """Test forward-forward positive pass."""
    from plato_cli import cmd_fflearn
    with patch('plato_cli.ForwardForwardLearner') as mock_learner:
        mock_instance = MagicMock()
        mock_instance.positive_pass.return_value = {'goodness': 0.7}
        mock_instance._goodness_to_level.return_value = 'proficient'
        mock_learner.return_value = mock_instance
        args = MockArgs(pass_type='positive', agent='oracle1', experience='test')
        cmd_fflearn(args)


def test_fflearn_status():
    """Test forward-forward learning status."""
    from plato_cli import cmd_fflearn
    with patch('plato_cli.ForwardForwardLearner') as mock_learner:
        mock_instance = MagicMock()
        mock_instance.get_learning_state.return_value = {
            'goodness': 0.6,
            'level': 'learning'
        }
        mock_learner.return_value = mock_instance
        args = MockArgs(pass_type='status', agent='oracle1', experience='')
        cmd_fflearn(args)


def test_swarm():
    """Test creative swarm command."""
    from plato_cli import cmd_swarm
    with patch('plato_cli.CreativeSwarm') as mock_swarm:
        mock_instance = MagicMock()
        mock_instance.generate.return_value = {
            'winner': {
                'temperature': 0.8,
                'text': 'Generated creative solution for fleet protocol...'
            },
            'pro_score': 0.85
        }
        mock_swarm.return_value = mock_instance
        args = MockArgs(prompt='Design a fleet protocol', deepinfra_key=None)
        cmd_swarm(args)


def test_reasoner():
    """Test dual-interpreter reasoner command."""
    from plato_cli import cmd_reasoner
    with patch('plato_cli.FluxReasoner') as mock_reasoner:
        mock_instance = MagicMock()
        mock_instance.reason_with_iterations.return_value = {
            'iterations': [
                {'gradient': 0.9, 'creative': 'Iteration 1 creative text...'},
                {'gradient': 0.5, 'creative': 'Iteration 2 creative text...'},
                {'gradient': 0.2, 'creative': 'Iteration 3 creative text...'},
            ],
            'final_gradient': 0.2,
            'converged': True
        }
        mock_reasoner.return_value = mock_instance
        args = MockArgs(prompt='Should we use async actors?')
        cmd_reasoner(args)


def test_dashboard():
    """Test dashboard command."""
    from plato_cli import cmd_dashboard
    with patch('plato_cli.FleetDashboard') as mock_dashboard:
        mock_instance = MagicMock()
        mock_instance.render_text.return_value = "Fleet Dashboard\n================"
        mock_dashboard.return_value = mock_instance
        args = MockArgs()
        cmd_dashboard(args)


def test_status():
    """Test status command."""
    from plato_cli import cmd_status
    with patch('plato_cli.FleetDashboard') as mock_dashboard, \
         patch('plato_cli.SurpriseDetector') as mock_detector, \
         patch('plato_cli.ForwardForwardLearner') as mock_learner:
        mock_dashboard.return_value.render_text.return_value = "Dashboard output"
        mock_detector.return_value.get_fleet_surprise.return_value = {
            'total_surprise': 1.0,
            'average_surprise': 0.3,
            'critical_agents': []
        }
        mock_learner.return_value.get_fleet_learning_state.return_value = {
            'fleet_goodness_avg': 0.65
        }
        args = MockArgs()
        cmd_status(args)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])