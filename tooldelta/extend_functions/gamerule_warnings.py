from ..constants import PacketIDS
from ..utils import fmts
from . import regist_extend_function
from .basic import ExtendFunction

@regist_extend_function
class GameruleWarnings(ExtendFunction):
    def __init__(self, frame):
        super().__init__(frame)
        self.sendcommandfeedback_was_disabled = False

    def when_activate(self):
        super().when_activate()

        def on_gamerule_changed(pk: dict):
            for rule in pk["GameRules"]:
                if rule["Name"] == "sendcommandfeedback":
                    if not rule["Value"]:
                        fmts.print_war("租赁服 sendcommandfeedback 被设置为 false")
                        self.sendcommandfeedback_was_disabled = True
                    elif self.sendcommandfeedback_was_disabled:
                        fmts.print_suc("租赁服 sendcommandfeedback 已被重新设置为 true")
                        self.sendcommandfeedback_was_disabled = False
            return False

        self.frame.packet_handler.add_dict_packet_listener(
            PacketIDS.GameRulesChanged, on_gamerule_changed
        )
