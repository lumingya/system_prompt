from astrbot.api.event import filter, AstrMessageEvent
from astrbot.api.star import Context, Star, register
from astrbot.api import logger

@register("custom_system_prompt", "your_name", "为LLM对话添加自定义系统提示词（支持头部和尾部）", "1.1.0")
class CustomSystemPromptPlugin(Star):
    def __init__(self, context: Context, config):
        """初始化插件
        
        Args:
            context: AstrBot上下文
            config: 插件配置对象
        """
        super().__init__(context)
        self.config = config

    @filter.on_llm_request(priority=9999)
    async def inject_prefix_prompt(self, event: AstrMessageEvent, req):
        """在最早时机注入头部提示词（priority=9999 确保最先执行）"""
        try:
            if not self.config.get('enable', True):
                return
            
            prefix_prompt = self.config.get('prefix_prompt', '').strip()
            if not prefix_prompt:
                return
            
            # 此时 system_prompt 应该是空的，直接设置
            current = req.system_prompt or ''
            separator = self.config.get('separator', '\n\n')
            
            if current:
                req.system_prompt = prefix_prompt + separator + current
            else:
                req.system_prompt = prefix_prompt
            
            logger.debug(f"[自定义提示词] 已注入头部，当前长度: {len(req.system_prompt)}")
            
        except Exception as e:
            logger.error(f"[自定义提示词] 头部注入错误: {e}")

    @filter.on_llm_request(priority=-9999)
    async def inject_suffix_prompt(self, event: AstrMessageEvent, req):
        """在最晚时机注入尾部提示词（priority=-9999 确保最后执行）"""
        try:
            if not self.config.get('enable', True):
                return
            
            suffix_prompt = self.config.get('suffix_prompt', '').strip()
            if not suffix_prompt:
                return
            
            # 此时所有插件和 AstrBot 核心都已处理完毕
            current = req.system_prompt or ''
            separator = self.config.get('separator', '\n\n')
            
            if current:
                req.system_prompt = current + separator + suffix_prompt
            else:
                req.system_prompt = suffix_prompt
            
            logger.debug(f"[自定义提示词] 已注入尾部，最终长度: {len(req.system_prompt)}")
            
        except Exception as e:
            logger.error(f"[自定义提示词] 尾部注入错误: {e}")

    async def terminate(self):
        """插件终止时清理资源"""
        pass