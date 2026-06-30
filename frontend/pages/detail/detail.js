Page({
  data: {
    statusBarHeight: 20,
    showE2: false,
    operator: {}
  },

  onLoad(options) {
    const sysInfo = wx.getSystemInfoSync();
    this.setData({
      statusBarHeight: sysInfo.statusBarHeight
    });
    
    // 使用提供的乌尔比安作为 Mock Data
    this.loadMockData();
  },

  goBack() {
    wx.navigateBack({
      delta: 1
    });
  },

  togglePortrait() {
    this.setData({ showE2: !this.data.showE2 });
  },

  loadMockData() {
    const mock = {
      character_id: "AA00",
      name: "乌尔比安",
      enName: "ULPIANUS", // Added Mock
      position: "近战位",    // Added Mock
      tags: "输出, 爆发, 生存", // Added Mock
      ranks: {             // Added Mock
        total: 5,
        idle: 4,
        burst: 6
      },
      character: {
        character_type: "重剑手",
        character_description: "同时攻击阻挡的所有敌人"
      },
      base_hp: 6022,
      base_atk: 1569,
      base_def: 0,
      base_res: 0,
      atk_time: 2.5,
      confidence_hp: 500,
      confidence_atk: 80,
      confidence_def: 0,
      confidence_res: 0,
      talents: [
        {
          talent_id: 0,
          talent_name: "本性的坚守",
          talent_decription: "每次受到伤害时，治疗自身100点生命值；生命值低于50%时，治疗效果提升至160点生命值"
        },
        {
          talent_id: 1,
          talent_name: "血脉的哺养",
          talent_decription: "每次击倒一名敌人时，自身的生命上限提高120，攻击力提高30，最多叠加9次，其他【深海猎人】干员生命上限60，攻击力15获得50%的提高效果"
        }
      ],
      skills: [
        {
          skill_id: 0,
          skill_name: "必须促成的接触",
          skill_type: "auto",
          duration: null,
          description: "向前方扔出船锚，船锚会把目标地点周围的两名敌人中等力度地拖拽至面前，对其造成相当于攻击力270%的物理伤害",
          start_sp: 0,
          consume_sp: 4,
          mockDps: "2450",
          mockDpsRank: "15",
          mockTotalDmg: "18000",
          mockTotalRank: "20",
          mockOverallRank: "18"
        },
        {
          skill_id: 1,
          skill_name: "必须维系的界限",
          skill_type: "auto",
          duration: null,
          description: "第一天赋的效果提升至2倍，阻挡数+1，生命上限+60%，攻击力+160%",
          start_sp: 0,
          consume_sp: 70,
          mockDps: "4500",
          mockDpsRank: "5",
          mockTotalDmg: "N/A",
          mockTotalRank: "N/A",
          mockOverallRank: "8"
        },
        {
          skill_id: 2,
          skill_name: "必须开辟的通路",
          skill_type: "manual",
          duration: 25,
          description: "最大生命值+80%，攻击力+260%，立即朝面前扔出一个船锚，撞击到目标或达到最远距离时停止，并对周围所有敌人造成攻击力160%的物理伤害和6秒晕眩。若船锚停留的位置可以部署，乌尔比安会移动到该位置。可以手动结束技能，技能结束时乌尔比安会返回到初始的位置",
          start_sp: 20,
          consume_sp: 25,
          mockDps: "6200",
          mockDpsRank: "3",
          mockTotalDmg: "155000",
          mockTotalRank: "4",
          mockOverallRank: "4"
        }
      ]
    };
    
    this.setData({
      operator: mock
    });
  }
});
