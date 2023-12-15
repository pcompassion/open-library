#!/usr/bin/env python3
from aiocron import crontab
from aiocron import Cron
from aiocron import wrap_func



class CronEx(Cron):

    def __init__(self, spec, func=None, args=(), kwargs=None, start=False,
                 uuid=None, loop=None, tz=None, croniter_kwargs=None, run_immediate=False):

        self.run_immediate = run_immediate
        self.has_run = False
        super().__init__(spec, func=func, args=args, kwargs=kwargs, start=start, uuid=uuid, loop=loop, tz=tz, croniter_kwargs=croniter_kwargs)

    def get_next(self):

        if not self.has_run and self.run_immediate:
            self.has_run = True
            return self.loop_time - 1
        else:
            return super().get_next()


def crontab(spec, func=None, args=(), kwargs=None, start=True, loop=None, tz=None, run_immediate=False):
    return CronEx(spec, func=func, args=args, kwargs=kwargs, start=start, loop=loop, tz=tz, run_immediate=run_immediate)
