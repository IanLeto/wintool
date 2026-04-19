#!/bin/bash
TARGET_DIR="/mnt/y/BaiduNetdiskDownload"
cd "$TARGET_DIR" || { echo "目录不存在！"; exit 1; }
OUTPUT="media_collection.json"
echo "[" > "$OUTPUT"
first=1

rename_and_add() {
    local old="$1"
    local new="$2"
    local cate="$3"
    if [ -d "$old" ]; then
        mv -n "$old" "$new"
        echo "✅ 重命名：$old -> $new"
    fi
    if [ $first -eq 1 ]; then
        first=0
    else
        echo "," >> "$OUTPUT"
    fi
    echo -n "{\"title\":\"$new\",\"category\":\"$cate\",\"status\":\"未看/未玩\"}" >> "$OUTPUT"
}

# 游戏
rename_and_add "3DMGAME-Final.Fantasy.VII.Remake.Intergrade-CODEX" "最终幻想7 重制版 间奏" "游戏"
rename_and_add "3DMGAME-Heroes.of.the.Three.Kingdoms.8.Steam-3DM" "三国志8" "游戏"
rename_and_add "3DMGAME-NieR.Replicant.ver.1.22474487139-3DM" "尼尔：人工生命 ver.1.22" "游戏"
rename_and_add "3DMGAME-Pathfinder_Wrath_of_the_Righteous-FLT" "开拓者：正义之怒" "游戏"
rename_and_add "3DMGAME-Sniper.Ghost.Warrior.Contracts.2.Deluxe.Arsenal.Edition.Cracked-3DM" "狙击手：幽灵战士 契约2 豪华版" "游戏"
rename_and_add "3DMGAME-Ys_IX_Monstrum_Nox-FLT" "伊苏9：怪人之夜" "游戏"
rename_and_add "Forspoken.v1.21" "魔咒之地 v1.21" "游戏"
rename_and_add "Ghost.of.Tsushima.DIRECTORS.CUT" "对马岛之魂 导演剪辑版" "游戏"
rename_and_add "Kingdom Come Deliverance II Mysteria Ecclesiae-v251113" "天国拯救2" "游戏"
rename_and_add "Ratchet.Clank.Rift.Apart.v1.726.0.0" "瑞奇与叮当：时空跳转" "游戏"
rename_and_add "Resident Evil 4" "生化危机4" "游戏"
rename_and_add "Resident Evil Village+DLC" "生化危机8：村庄+DLC" "游戏"
rename_and_add "StellarBlade" "星刃" "游戏"
rename_and_add "W 文明6_v1.0.12.68 附345合集-赠九只气球七大奇观罗马辐射投石空运存档+音乐原声+多项修改器" "文明6 完整版" "游戏"
rename_and_add "八方旅人" "八方旅人" "游戏"
rename_and_add "勇战r3.06内嵌汉化" "勇战 r3.06 汉化版" "游戏"
rename_and_add "卧龙苍天陨落1.304学习资源" "卧龙苍天陨落 v1.304" "游戏"
rename_and_add "合金装备5：幻痛 3DM首发中文破解版V2" "合金装备5：幻痛 V2" "游戏"
rename_and_add "堕落之主" "堕落之主" "游戏"
rename_and_add "寂静岭f" "寂静岭f" "游戏"
rename_and_add "对马岛" "对马岛之魂" "游戏"
rename_and_add "巫师3 次世代版" "巫师3 次世代版" "游戏"
rename_and_add "怪物猎人" "怪物猎人" "游戏"
rename_and_add "战神5" "战神5：诸神黄昏" "游戏"
rename_and_add "星露谷物语" "星露谷物语" "游戏"
rename_and_add "最后生还者2重置版" "最后生还者2 重置版" "游戏"
rename_and_add "最后生还者重置版" "最后生还者 重置版" "游戏"
rename_and_add "最终幻想16" "最终幻想16" "游戏"
rename_and_add "最终幻想：13雷霆归来集成3号升级档全DLC   繁中" "最终幻想13：雷霆归来 全DLC 繁中" "游戏"
rename_and_add "波斯王子" "波斯王子" "游戏"
rename_and_add "消逝的光芒2" "消逝的光芒2" "游戏"
rename_and_add "漫威蜘蛛侠2-数字豪华版" "漫威蜘蛛侠2 数字豪华版" "游戏"
rename_and_add "潜水员戴夫" "潜水员戴夫" "游戏"
rename_and_add "祇：女神之道" "祇：女神之道" "游戏"
rename_and_add "空洞骑士" "空洞骑士" "游戏"
rename_and_add "质量效应3集成高清材质包MODV1.5.5427.124   汉化中文" "质量效应3 高清材质 MOD 汉化版" "游戏"
rename_and_add "质量效应集成高清材质包MODV1.0.2  全DLC   汉化中文Mass Effect 2.part1" "质量效应2 高清材质 全DLC 汉化版" "游戏"
rename_and_add "鏡の魔" "镜之魔女" "游戏"
rename_and_add "霍格沃茨之遗" "霍格沃茨之遗" "游戏"
rename_and_add "霍格沃茨之遗200+MOD" "霍格沃茨之遗 200+MOD 版" "游戏"
rename_and_add "骑马与砍杀2：霸主" "骑马与砍杀2：霸主" "游戏"

# 影视
rename_and_add "4K（全8集）中英.小人" "小人 4K 全8集" "电视剧"
rename_and_add "国产悬疑巅峰三部曲（4K+1080P）全36集" "国产悬疑巅峰三部曲 全36集" "电视剧"

echo "" >> "$OUTPUT"
echo "]" >> "$OUTPUT"
echo -e "\n🎉 全部完成！"
echo -e "📁 目录已重命名"
echo -e "📄 清单已生成：$TARGET_DIR/media_collection.json"