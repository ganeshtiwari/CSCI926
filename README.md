# CSCI926
Project Repo for CSCI926 (Software Testing)

# Resources 
[Week 1 slide](https://docs.google.com/presentation/d/1BnmPHccQ5xg8k5IJvG6wIy1oJznhBIennWBR5TcS-5c/edit#slide=id.p)

# Task 2 
1. Tools Choice 
  - [Unit Test - Pytest](https://docs.pytest.org/en/8.0.x/)
  - [Unit Test - UnitTest](https://docs.python.org/3/library/unittest.html)
  - [Mock Test - Mock](https://pypi.org/project/mock/)
  - [Ui Test - PyAutoGUI](https://pypi.org/project/PyAutoGUI/)
  - [Code Analysis - Ruff](https://github.com/astral-sh/ruff)

2. Application Choice
  - [Exaile](https://github.com/exaile/exaile?tab=readme-ov-file) [site](https://exaile.org/)


## Notes
queue.py
```
def get_next(self):
        """
        Retrieves the next track that will be played. Does not
        actually set the position. When you call next(), it should
        return the same track.

        This exists to support retrieving a track before it actually
        needs to be played, such as for pre-buffering.

        :returns: the next track to be played
        :rtype: :class:`xl.trax.Track` or None
        """
        if self.__queue_has_tracks and len(self):
            track = self._calculate_next_track()
            if track is not None:
                return track
        
        # None check skipped, leading to call of get_next() on None when # self.current_playlist is None
        if self.current_playlist is not self: 
            return self.current_playlist.get_next()
        elif self.last_playlist is not None:
            return self.last_playlist.get_next()
        else:
            return None
```