import React from 'react';
import Tippy from '@tippyjs/react';
import 'tippy.js/dist/tippy.css';

const Tooltip = ({ 
  children, 
  content, 
  placement = "top",
  animation = "scale",
  duration = [200, 150],
  arrow = true,
  delay = [100, 0],
  interactive = false,
  ...props 
}) => {
  return (
    <Tippy
      content={content}
      placement={placement}
      animation={animation}
      duration={duration}
      arrow={arrow}
      delay={delay}
      interactive={interactive}
      appendTo={() => document.body}
      popperOptions={{
        modifiers: [
          {
            name: 'offset',
            options: {
              offset: [0, 8],
            },
          },
        ],
      }}
      onShow={(instance) => {
        // Apply custom styles directly to the tooltip element
        const tooltip = instance.popper.querySelector('.tippy-box');
        const isDark = document.documentElement.classList.contains('dark');
        
        if (tooltip) {
          tooltip.style.cssText = `
            background: ${isDark ? 'rgba(31, 41, 55, 0.95)' : 'rgba(255, 255, 255, 0.95)'} !important;
            backdrop-filter: blur(20px) !important;
            -webkit-backdrop-filter: blur(20px) !important;
            border: 1px solid ${isDark ? 'rgba(255, 255, 255, 0.2)' : 'rgba(255, 255, 255, 0.4)'} !important;
            border-radius: 12px !important;
            box-shadow: 0 10px 25px -5px rgba(0, 0, 0, ${isDark ? '0.4' : '0.15'}), 
                        0 4px 10px -5px rgba(0, 0, 0, ${isDark ? '0.2' : '0.1'}),
                        inset 0 1px 0 rgba(255, 255, 255, 0.1) !important;
            color: ${isDark ? '#f9fafb' : '#1f2937'} !important;
            font-size: 14px !important;
            font-weight: 500 !important;
            padding: 0 !important;
          `;
        }

        const content = instance.popper.querySelector('.tippy-content');
        if (content) {
          content.style.cssText = `
            padding: 12px 16px !important;
            line-height: 1.5 !important;
            font-family: inherit !important;
          `;
        }

        const arrow = instance.popper.querySelector('.tippy-arrow');
        if (arrow) {
          arrow.style.color = isDark ? 'rgba(31, 41, 55, 0.95)' : 'rgba(255, 255, 255, 0.95)';
        }
      }}
      {...props}
    >
      {children}
    </Tippy>
  );
};

export default Tooltip;