import unittest
from pathlib import Path

from producao.timeline import build_timeline, frame_at

ROOT = Path(__file__).resolve().parents[1]


class TimelineTests(unittest.TestCase):
    def test_all_twelve_clips_are_complete_and_separated(self):
        timeline = build_timeline(ROOT)
        self.assertEqual(len(timeline['dialogue']), 12)
        for a, b in zip(timeline['dialogue'], timeline['dialogue'][1:]):
            self.assertLessEqual(a['end'] + .59, b['start'])
        for clip in timeline['dialogue']:
            self.assertGreater(clip['end'] - clip['start'], 1)
            self.assertTrue((ROOT / clip['path']).is_file())
            self.assertTrue(any(v > .01 for v in clip['envelope']))

    def test_story_has_time_for_actions_and_goodbye(self):
        t = build_timeline(ROOT)
        self.assertGreaterEqual(t['events']['care_end'] - t['events']['plant_start'], 10)
        self.assertLess(t['events']['plant_end'], t['events']['magic_start'])
        self.assertGreaterEqual(t['duration'] - t['dialogue'][-1]['end'], 4)
        self.assertEqual(t['frames'], frame_at(t['duration']) - 1)

    def test_frame_zero_is_one_and_seconds_are_exact(self):
        self.assertEqual(frame_at(0), 1)
        self.assertEqual(frame_at(1), 13)

    def test_missing_audio_does_not_silently_drop_dialogue(self):
        with self.assertRaises(FileNotFoundError):
            build_timeline(Path('/tmp/nonexistent-clareira-fixture'))


if __name__ == '__main__':
    unittest.main()
