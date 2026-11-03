WushanStation_MapScripts::
	map_script MAP_SCRIPT_ON_FRAME_TABLE, WushanStation_OnFrame
	.byte 0

WushanStation_OnFrame:
	map_script_2 VAR_TEMP_0, 0, WushanStation_EventScript_Intro
	.2byte 0

WushanStation_EventScript_Intro::
	goto_if_set FLAG_INTRO_SEEN, WushanStation_EventScript_IntroSkip
	lockall
	msgbox WushanStation_Text_Intro, MSGBOX_DEFAULT
	setflag FLAG_INTRO_SEEN
	setflag FLAG_SYS_B_DASH
	setvar VAR_TEMP_0, 1
	releaseall
	end

WushanStation_EventScript_IntroSkip::
	setvar VAR_TEMP_0, 1
	end

WushanStation_EventScript_Lan::
	lock
	faceplayer
	setspeaker WushanStation_Text_NameLan
	goto_if_set FLAG_GOT_STARTER, WushanStation_EventScript_LanRepeat
	msgbox WushanStation_Text_LanFirst, MSGBOX_DEFAULT
	setspeaker WushanStation_Text_NameLan
	msgbox WushanStation_Text_LanBeforeChoice, MSGBOX_DEFAULT
	dynmultichoice 0, 0, FALSE, 3, 0, DYN_MULTICHOICE_CB_NONE, WushanStation_Text_ChoiceTreecko, WushanStation_Text_ChoiceTorchic, WushanStation_Text_ChoiceMudkip
	switch VAR_RESULT
	case 0, WushanStation_EventScript_GiveTreecko
	case 1, WushanStation_EventScript_GiveTorchic
	case 2, WushanStation_EventScript_GiveMudkip
	release
	end

WushanStation_EventScript_GiveTreecko::
	setspeaker WushanStation_Text_NameLan
	msgbox WushanStation_Text_LanTreecko, MSGBOX_DEFAULT
	bufferspeciesname STR_VAR_1, SPECIES_TREECKO
	givemon SPECIES_TREECKO, 5
	goto WushanStation_EventScript_AfterGive

WushanStation_EventScript_GiveTorchic::
	setspeaker WushanStation_Text_NameLan
	msgbox WushanStation_Text_LanTorchic, MSGBOX_DEFAULT
	bufferspeciesname STR_VAR_1, SPECIES_TORCHIC
	givemon SPECIES_TORCHIC, 5
	goto WushanStation_EventScript_AfterGive

WushanStation_EventScript_GiveMudkip::
	setspeaker WushanStation_Text_NameLan
	msgbox WushanStation_Text_LanMudkip, MSGBOX_DEFAULT
	bufferspeciesname STR_VAR_1, SPECIES_MUDKIP
	givemon SPECIES_MUDKIP, 5
	goto WushanStation_EventScript_AfterGive

WushanStation_EventScript_AfterGive::
	goto_if_eq VAR_RESULT, MON_CANT_GIVE, Common_EventScript_NoMoreRoomForPokemon
	setflag FLAG_GOT_STARTER
	setflag FLAG_TALKED_LAN
	setflag FLAG_SYS_POKEMON_GET
	setflag FLAG_SYS_POKEDEX_GET
	playfanfare MUS_LEVEL_UP
	msgbox WushanStation_Text_ReceivedPartner, MSGBOX_DEFAULT
	waitfanfare
	giveitem ITEM_POKE_BALL, 5
	setspeaker WushanStation_Text_NameLan
	msgbox WushanStation_Text_LanPointNorth, MSGBOX_DEFAULT
	release
	end

WushanStation_EventScript_LanRepeat::
	msgbox WushanStation_Text_LanRepeat, MSGBOX_DEFAULT
	release
	end

WushanStation_EventScript_You::
	lock
	faceplayer
	setspeaker WushanStation_Text_NameYou
	msgbox WushanStation_Text_You, MSGBOX_DEFAULT
	release
	end

WushanStation_EventScript_Doudou::
	lock
	faceplayer
	setspeaker WushanStation_Text_NameDoudou
	msgbox WushanStation_Text_Doudou, MSGBOX_DEFAULT
	release
	end

WushanStation_EventScript_Guard::
	lock
	faceplayer
	setspeaker WushanStation_Text_NameGuard
	goto_if_set FLAG_GOT_STARTER, WushanStation_EventScript_GuardPass
	msgbox WushanStation_Text_GuardStop, MSGBOX_DEFAULT
	release
	end

WushanStation_EventScript_GuardPass::
	msgbox WushanStation_Text_GuardPass, MSGBOX_DEFAULT
	release
	end

WushanStation_EventScript_NorthDoor::
	goto_if_set FLAG_GOT_STARTER, WushanStation_EventScript_NorthDoorOpen
	lockall
	setspeaker WushanStation_Text_NameGuard
	msgbox WushanStation_Text_GuardStop, MSGBOX_DEFAULT
	applymovement LOCALID_PLAYER, WushanStation_Movement_StepSouth
	waitmovement 0
	releaseall
	end

WushanStation_EventScript_NorthDoorOpen::
	end

WushanStation_Movement_StepSouth:
	walk_down
	step_end

WushanStation_Text_NameLan:
	.string "南极仙翁$"

WushanStation_Text_NameYou:
	.string "You$"

WushanStation_Text_NameDoudou:
	.string "Doudou$"

WushanStation_Text_NameGuard:
	.string "Guard$"

WushanStation_Text_Intro:
	.string "The fog is heavy.\p"
	.string "Ahead is 雾杉驿站.$"

WushanStation_Text_LanFirst:
	.string "You walked out of the fog?\p"
	.string "You made it this far.\n"
	.string "Your legs are fine.\p"
	.string "The fog past the station\n"
	.string "is thicker.\p"
	.string "Going in empty-handed\n"
	.string "won't do.\p"
	.string "Pick a partner.\p"
	.string "All three are here.\n"
	.string "You choose.$"

WushanStation_Text_LanBeforeChoice:
	.string "Think it through\n"
	.string "before you take one.\p"
	.string "Once you take it, you walk\n"
	.string "this road together.$"

WushanStation_Text_ChoiceTreecko:
	.string "野猪$"

WushanStation_Text_ChoiceTorchic:
	.string "海毛虫$"

WushanStation_Text_ChoiceMudkip:
	.string "巨蛙$"

WushanStation_Text_LanTreecko:
	.string "野猪. Steady.\n"
	.string "It can bear the fog.\p"
	.string "Look after it.$"

WushanStation_Text_LanTorchic:
	.string "海毛虫. Impatient,\n"
	.string "and full of fire.\p"
	.string "Look after it.$"

WushanStation_Text_LanMudkip:
	.string "巨蛙. Calm.\n"
	.string "You can count on it.\p"
	.string "Look after it.$"

WushanStation_Text_ReceivedPartner:
	.string "{PLAYER} received {STR_VAR_1}.$"

WushanStation_Text_LanPointNorth:
	.string "It's with you.\p"
	.string "North of here is the\n"
	.string "雾杉外缘.\p"
	.string "Don't wander in the fog.\p"
	.string "I'll be here when you\n"
	.string "come back.$"

WushanStation_Text_LanRepeat:
	.string "雾杉外缘\n"
	.string "is to the north.\p"
	.string "If you can't win,\n"
	.string "come back first.$"

WushanStation_Text_You:
	.string "What you meet on the road,\n"
	.string "the field guide will record.\p"
	.string "If you're tired, save.\n"
	.string "Don't force it.\p"
	.string "The fog on 雾杉外缘\n"
	.string "lifts slowly.\p"
	.string "Walk a bit. Look around.$"

WushanStation_Text_Doudou:
	.string "Something's moving\n"
	.string "in the fog.\p"
	.string "You're going into\n"
	.string "the fog too?$"

WushanStation_Text_GuardStop:
	.string "Stop.\p"
	.string "No partner, no leaving\n"
	.string "through this door.\p"
	.string "Go find 南极仙翁.$"

WushanStation_Text_GuardPass:
	.string "You have a partner?\p"
	.string "All right. Go on.\p"
	.string "The fog is thick.\n"
	.string "Walk steady.$"
