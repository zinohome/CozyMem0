"use client";

import { useState, useEffect } from "react";
import { useSelector, useDispatch } from "react-redux";
import { RootState, AppDispatch } from "@/store/store";
import { setUserId } from "@/store/profileSlice";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { User, Check } from "lucide-react";
import { useToast } from "@/components/ui/use-toast";

// 常用用户列表（可以从 API 获取或配置）
const COMMON_USERS = [
  "user",
  "admin",
  "test",
  "demo",
];

export function UserSelector() {
  const dispatch = useDispatch<AppDispatch>();
  const { toast } = useToast();
  const currentUserId = useSelector((state: RootState) => state.profile.userId);
  const [open, setOpen] = useState(false);
  const [inputValue, setInputValue] = useState(currentUserId);
  const [recentUsers, setRecentUsers] = useState<string[]>([]);

  // 从 localStorage 加载最近使用的用户
  useEffect(() => {
    const stored = localStorage.getItem("mem0_recent_users");
    if (stored) {
      try {
        setRecentUsers(JSON.parse(stored));
      } catch (e) {
        // 忽略解析错误
      }
    }
  }, []);

  // 同步 inputValue 与 currentUserId
  useEffect(() => {
    setInputValue(currentUserId);
  }, [currentUserId]);

  const handleUserChange = (userId: string) => {
    if (!userId.trim()) {
      toast({
        title: "Invalid User ID",
        description: "User ID cannot be empty",
        variant: "destructive",
      });
      return;
    }

    // 更新 Redux store
    dispatch(setUserId(userId.trim()));

    // 保存到 localStorage
    localStorage.setItem("mem0_user_id", userId.trim());

    // 更新最近使用的用户列表
    const updated = [
      userId.trim(),
      ...recentUsers.filter((u) => u !== userId.trim()),
    ].slice(0, 5); // 只保留最近5个
    setRecentUsers(updated);
    localStorage.setItem("mem0_recent_users", JSON.stringify(updated));

    setOpen(false);
    toast({
      title: "User ID Updated",
      description: `Switched to user: ${userId.trim()}`,
    });
  };

  const handleInputSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleUserChange(inputValue);
  };

  // 合并常用用户和最近使用的用户
  const allUsers = [
    ...new Set([...recentUsers, ...COMMON_USERS, currentUserId]),
  ];

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <Button
          variant="outline"
          size="sm"
          className="border-zinc-700/50 bg-zinc-900 hover:bg-zinc-800 text-zinc-300"
        >
          <User className="mr-2 h-4 w-4" />
          <span className="max-w-[100px] truncate">{currentUserId}</span>
        </Button>
      </PopoverTrigger>
      <PopoverContent className="w-80 bg-zinc-900 border-zinc-800">
        <div className="space-y-4">
          <div>
            <Label className="text-zinc-300 mb-2 block">Current User</Label>
            <div className="flex items-center gap-2 p-2 bg-zinc-800 rounded-md">
              <User className="h-4 w-4 text-zinc-400" />
              <span className="text-white font-medium">{currentUserId}</span>
              <Check className="h-4 w-4 text-green-500 ml-auto" />
            </div>
          </div>

          <form onSubmit={handleInputSubmit} className="space-y-2">
            <Label htmlFor="user-input" className="text-zinc-300">
              Enter User ID
            </Label>
            <div className="flex gap-2">
              <Input
                id="user-input"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Enter user ID..."
                className="bg-zinc-800 border-zinc-700 text-white placeholder:text-zinc-500"
                autoFocus
              />
              <Button
                type="submit"
                size="sm"
                className="bg-primary hover:bg-primary/90"
              >
                Apply
              </Button>
            </div>
          </form>

          {allUsers.length > 0 && (
            <div>
              <Label className="text-zinc-300 mb-2 block">
                Quick Select
              </Label>
              <div className="flex flex-wrap gap-2">
                {allUsers.map((userId) => (
                  <Button
                    key={userId}
                    variant="outline"
                    size="sm"
                    onClick={() => handleUserChange(userId)}
                    className={`border-zinc-700 text-zinc-300 hover:bg-zinc-800 ${
                      userId === currentUserId
                        ? "bg-zinc-800 border-zinc-600"
                        : ""
                    }`}
                  >
                    {userId}
                  </Button>
                ))}
              </div>
            </div>
          )}
        </div>
      </PopoverContent>
    </Popover>
  );
}

