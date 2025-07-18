import * as React from "react"
import { cn } from "../../lib/utils.js"

const buttonVariants = {
  variant: {
    default: "bg-gradient-primary text-white shadow-lg shadow-primary/25 hover:shadow-xl hover:shadow-primary/30 hover:scale-105",
    secondary: "bg-gradient-secondary text-white shadow-lg shadow-secondary/25 hover:shadow-xl hover:shadow-secondary/30 hover:scale-105",
    glass: "bg-glass-light dark:bg-glass-dark-light backdrop-blur-md border border-white/20 dark:border-white/10 text-gray-700 dark:text-gray-200 shadow-glass hover:bg-glass-light/80 dark:hover:bg-glass-dark-light/80 hover:shadow-glass-inset",
    ghost: "hover:bg-gray-100/10 dark:hover:bg-gray-800/20 hover:backdrop-blur-sm text-gray-700 dark:text-gray-300",
    outline: "border border-gray-300 dark:border-gray-600 bg-transparent hover:bg-gray-100/10 dark:hover:bg-gray-800/20 hover:backdrop-blur-sm text-gray-700 dark:text-gray-300",
  },
  size: {
    default: "h-10 px-4 py-2",
    sm: "h-9 px-3",
    lg: "h-11 px-8",
    icon: "h-10 w-10",
  },
}

const Button = React.forwardRef(({ 
  className, 
  variant = "default", 
  size = "default", 
  asChild = false, 
  ...props 
}, ref) => {
  const Comp = asChild ? "div" : "button"
  return (
    <Comp
      className={cn(
        "inline-flex items-center justify-center whitespace-nowrap rounded-xl text-sm font-medium transition-all duration-300 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
        buttonVariants.variant[variant],
        buttonVariants.size[size],
        className
      )}
      ref={ref}
      {...props}
    />
  )
})
Button.displayName = "Button"

export { Button }