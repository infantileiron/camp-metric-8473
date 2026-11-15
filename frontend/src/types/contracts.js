/** @typedef {{id:number,code:string,version:number,name:string,numerator:string,denominator:string,locked:boolean}} Metric */
/** @typedef {{id:number,class_code:string,day:string,mode:string,enrolled:number,attended:number,completed:number,refunds:number}} Fact */
/** @typedef {{id:number,metric_id:number,state:string,result:object,approval:string,note:string}} Snapshot */
/** @typedef {{id:number,snapshot_id:number,state:string,date_from:string,date_to:string,metric:object,signed:object,numerator:number,denominator:number,value:number|null,groups:Array,applied_event_id:number,backlog:number,caught_up:boolean,delta_value:number|null,error:string,updated:string}} Tracker */
