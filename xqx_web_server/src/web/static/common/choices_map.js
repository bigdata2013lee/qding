(function($){
    
    var ch = qd.nameSpace("choices");
    
    ch.genders={M:'男', W:'女', F:'女'};
    ch.levels={'system':'系统', 'manager':'管理员', 'common':'普通'};
    ch.alarm_types={1: "紧急", 2: "红外", 3: "燃气", 4: "门磁", 5: "窗磁", 6: "烟感", 7: "破坏"};
    ch.gate_types = {'Gate.UnitGate': '单元门口机', 'Gate.FenceGate': '围墙门口机'};
    ch.review_types = {'new': '未审核', 'reject': '拒绝', 'pass': '通过'};
    ch.device_types = {'UnitGate': '单元门口机', 'FenceGate': '围墙门口机','AlarmGateway': '报警网关', 'AioManager': '管理中心机'};

})(jQuery);