# step_utils.py
import json
from telegram_bot_platform.compat.logging_ext.logger import CustomLogger

# step_handler_mixin.py
class StepHandlerMixin:
        
    
        
    edit_ad_steps = [
       {"name": "edit_start_time", "prompt": "🕒 لطفاً ساعت جدید شروع آگهی را وارد کنید (مثال: 14:00)"},
       {"name": "edit_end_time", "prompt": "🕓 لطفاً ساعت جدید پایان آگهی را وارد کنید (مثال: 18:00)"},
       {"name": "edit_service_count", "prompt": "🔢 لطفاً تعداد جدید سرویس‌های قابل پذیرش را وارد کنید:"},
       {"name": "edit_description", "prompt": "📝 لطفاً توضیح جدید آگهی را وارد کنید (یا بنویسید 'ندارد'):"},
    ]


    def get_step_by_name(self, section, step_name):
        steps = getattr(self, f"{section}_steps", [])
        for step in steps:
            if step["name"] == step_name:
                return step
        return None

    def execute_next_step(self, message, section):
   
        # logger = logging.getLogger("StepHandler")
        chat_id = message.chat.id

        user_data = self.data.setdefault(chat_id, {}).setdefault(section, {})
        workflow = user_data.get("workflow", [])
        step_index = user_data.get("step_index", 0)

        while step_index < len(workflow):
            step_name = workflow[step_index]
            user_data["step_index"] = step_index + 1  # move to next

            step_def = self.get_step_by_name(section, step_name)

            # Internal implementation note: legacy behavior is preserved during modernization.
            if "conditional" in step_def:
                condition = step_def["conditional"]
                cond_field = condition.get("field")
                cond_value = condition.get("value")
                current_val = user_data.get(cond_field)

                if current_val != cond_value:
                    # Internal implementation note: legacy behavior is preserved during modernization.
                    step_index += 1
                    continue

            # Internal implementation note: legacy behavior is preserved during modernization.
            return getattr(self, step_name)(message)

    # Internal implementation note: legacy behavior is preserved during modernization.
            logger.info(f"✅ {section.upper()} COMPLETE [{chat_id}]: {json.dumps(self.data[chat_id], ensure_ascii=False, indent=2)}")
            self.bot.send_message(chat_id, "✅ تمامی مراحل تکمیل شدند!")

        
        
        
        
        

    def execute_current_step(self, message, section):
        chat_id = message.chat.id
        workflow = self.data.get(chat_id, {}).get(section, {}).get("workflow", [])
        step_index = self.data.get(chat_id, {}).get(section, {}).get("step_index", 0)
    
        if step_index == 0:
            step_name = workflow[0]
        else:
            step_name = workflow[step_index - 1]
    
        getattr(self, step_name)(message)