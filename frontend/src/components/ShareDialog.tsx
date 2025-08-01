import { useState } from 'react'
import {
  Dialog,
  DialogDescription,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
  DialogPortal,
  DialogOverlay,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Share2,
  Copy,
  Check,
  MessageCircle,
  Mail,
  Twitter,
  Facebook,
  Linkedin,
  X
} from 'lucide-react'
import { useToast } from '@/hooks/useToast.ts'
import * as DialogPrimitive from "@radix-ui/react-dialog"

interface ShareDialogProps {
  playlistName: string
  children: React.ReactNode
}

export function ShareDialog({ playlistName, children }: ShareDialogProps) {
  const [copied, setCopied] = useState(false)
  const [open, setOpen] = useState(false)
  const { toast } = useToast()

  const currentUrl = typeof window !== 'undefined' ? window.location.href : ''
  const shareText = `Check out this playlist: "${playlistName}" 🎵`

  const handleCopyLink = async () => {
    try {
      await navigator.clipboard.writeText(currentUrl)
      setCopied(true)
      toast({
        title: "Link copied!",
        description: "Playlist link has been copied to your clipboard.",
        duration: 3000,
      })

      // Reset copied state after 2 seconds
      setTimeout(() => setCopied(false), 2000)
    } catch (err) {
      console.error('Failed to copy to clipboard:', err)
      toast({
        title: "Failed to copy",
        description: "Could not copy link to clipboard. Please copy the URL manually.",
        variant: "destructive",
        duration: 3000,
      })
    }
  }

  const shareOptions = [
    {
      name: 'WhatsApp',
      icon: MessageCircle,
      url: `https://wa.me/?text=${encodeURIComponent(`${shareText} ${currentUrl}`)}`,
      color: 'hover:bg-green-50 hover:text-green-600 dark:hover:bg-green-950',
    },
    {
      name: 'Twitter',
      icon: Twitter,
      url: `https://twitter.com/intent/tweet?text=${encodeURIComponent(shareText)}&url=${encodeURIComponent(currentUrl)}`,
      color: 'hover:bg-blue-50 hover:text-blue-600 dark:hover:bg-blue-950',
    },
    {
      name: 'Facebook',
      icon: Facebook,
      url: `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(currentUrl)}`,
      color: 'hover:bg-blue-50 hover:text-blue-700 dark:hover:bg-blue-950',
    },
    {
      name: 'LinkedIn',
      icon: Linkedin,
      url: `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(currentUrl)}`,
      color: 'hover:bg-blue-50 hover:text-blue-600 dark:hover:bg-blue-950',
    },
    {
      name: 'Email',
      icon: Mail,
      url: `mailto:?subject=${encodeURIComponent(`Check out this playlist: ${playlistName}`)}&body=${encodeURIComponent(`${shareText}\n\n${currentUrl}`)}`,
      color: 'hover:bg-gray-50 hover:text-gray-700 dark:hover:bg-gray-950',
    },
  ]

  const handleSocialShare = (url: string) => {
    window.open(url, '_blank', 'noopener,noreferrer,width=600,height=400')
  }

  return (
    <Dialog open={open} onOpenChange={setOpen}>
      <DialogTrigger asChild>
        {children}
      </DialogTrigger>
      <DialogPortal>
        <DialogOverlay className="fixed inset-0 z-50 bg-black/80 data-[state=open]:animate-in data-[state=closed]:animate-out data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0" />
        <DialogPrimitive.Content
          style={{
            position: 'fixed',
            top: '50%',
            left: '50%',
            transform: 'translate(-50%, -50%)',
            zIndex: 51,
            width: '90vw',
            maxWidth: '28rem',
            maxHeight: '90vh',
            overflowY: 'auto',
            backgroundColor: 'hsl(var(--background))',
            border: '1px solid hsl(var(--border))',
            borderRadius: '0.5rem',
            padding: '1.5rem',
            boxShadow: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
          }}
        >
          <DialogHeader className="mb-6">
            <DialogTitle className="flex items-center gap-2 text-lg font-semibold">
              <Share2 className="w-5 h-5" />
              Share Playlist
            </DialogTitle>
            <DialogDescription className="text-sm text-muted-foreground">
              Share "{playlistName}" with your friends and family.
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-6">
            {/* Copy Link Section */}
            <div className="space-y-2">
              <Label htmlFor="link">Copy Link</Label>
              <div className="flex gap-2">
                <Input
                  id="link"
                  value={currentUrl}
                  readOnly
                  className="flex-1 text-sm"
                />
                <Button
                  onClick={handleCopyLink}
                  variant={copied ? "default" : "outline"}
                  className="px-3 shrink-0"
                >
                  {copied ? (
                    <Check className="w-4 h-4" />
                  ) : (
                    <Copy className="w-4 h-4" />
                  )}
                </Button>
              </div>
            </div>

            {/* Social Sharing Options */}
            <div className="space-y-3">
              <Label>Share on Social Media</Label>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                {shareOptions.map((option) => {
                  const Icon = option.icon
                  return (
                    <Button
                      key={option.name}
                      variant="outline"
                      onClick={() => handleSocialShare(option.url)}
                      className={`justify-start gap-3 h-12 ${option.color}`}
                    >
                      <Icon className="w-5 h-5" />
                      {option.name}
                    </Button>
                  )
                })}
              </div>
            </div>

            {/* Note about sharing */}
            <div className="text-sm text-muted-foreground bg-muted/50 p-3 rounded-lg">
              <p>
                💡 <strong>Tip:</strong> Anyone with this link will be able to view the playlist
                and save it to their own collection.
              </p>
            </div>
          </div>

          {/* Close button */}
          <DialogPrimitive.Close className="absolute right-4 top-4 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2 disabled:pointer-events-none data-[state=open]:bg-accent data-[state=open]:text-muted-foreground">
            <X className="h-4 w-4" />
            <span className="sr-only">Close</span>
          </DialogPrimitive.Close>
        </DialogPrimitive.Content>
      </DialogPortal>
    </Dialog>
  )
}